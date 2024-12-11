import sqlite3
import argparse
import os
import sys
import shutil
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from ra_aid.tools import (
    ask_expert, run_shell_command, run_programming_task,
    emit_research_notes, emit_plan, emit_related_files, emit_task,
    emit_expert_context, get_memory_value, emit_key_facts, delete_key_facts,
    emit_key_snippets, delete_key_snippets,
    request_implementation, read_file_tool, emit_research_subtask,
    fuzzy_find_project_files, ripgrep_search, list_directory_tree
)
from ra_aid.tools.memory import _global_memory
from ra_aid import print_agent_output, print_stage_header, print_task_header
from ra_aid.tools.programmer import related_files
from ra_aid.prompts import (
    RESEARCH_PROMPT,
    PLANNING_PROMPT,
    IMPLEMENTATION_PROMPT,
    SUMMARY_PROMPT
)
from ra_aid.exceptions import TaskCompletedException

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='RA.Aid - AI Agent for executing programming and research tasks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    ra-aid -m "Add error handling to the database module"
    ra-aid -m "Explain the authentication flow" --research-only
        '''
    )
    parser.add_argument(
        '-m', '--message',
        type=str,
        required=True,
        help='The task or query to be executed by the agent'
    )
    parser.add_argument(
        '--research-only',
        action='store_true',
        help='Only perform research without implementation'
    )
    parser.add_argument(
        '--cowboy-mode',
        action='store_true',
        help='Skip interactive approval for shell commands'
    )
    return parser.parse_args()

# Create the base model
model = ChatAnthropic(model_name="claude-3-5-sonnet-20241022")

# Create individual memory objects for each agent
research_memory = MemorySaver()
planning_memory = MemorySaver()
implementation_memory = MemorySaver()

# Define tool sets for each stage
research_tools = [list_directory_tree, emit_research_subtask, run_shell_command, emit_expert_context, ask_expert, emit_research_notes, emit_related_files, emit_key_facts, delete_key_facts, emit_key_snippets, delete_key_snippets, request_implementation, read_file_tool, fuzzy_find_project_files, ripgrep_search]
planning_tools = [list_directory_tree, emit_expert_context, ask_expert, emit_plan, emit_task, emit_related_files, emit_key_facts, delete_key_facts, emit_key_snippets, delete_key_snippets, read_file_tool, fuzzy_find_project_files, ripgrep_search]
implementation_tools = [list_directory_tree, run_shell_command, emit_expert_context, ask_expert, run_programming_task, emit_related_files, emit_key_facts, delete_key_facts, emit_key_snippets, delete_key_snippets, read_file_tool, fuzzy_find_project_files, ripgrep_search]

# Create stage-specific agents with individual memory objects
research_agent = create_react_agent(model, research_tools, checkpointer=research_memory)
planning_agent = create_react_agent(model, planning_tools, checkpointer=planning_memory)
implementation_agent = create_react_agent(model, implementation_tools, checkpointer=implementation_memory)


def is_informational_query() -> bool:
    """Determine if the current query is informational based on implementation_requested state.
    
    Returns:
        bool: True if query is informational (no implementation requested), False otherwise
    """
    # Check both the research_only flag and implementation_requested state
    return _global_memory.get('config', {}).get('research_only', False) or not is_stage_requested('implementation')

def is_stage_requested(stage: str) -> bool:
    """Check if a stage has been requested to proceed.
    
    Args:
        stage: The stage to check ('implementation')
        
    Returns:
        True if the stage was requested, False otherwise
    """
    if stage == 'implementation':
        return len(_global_memory.get('implementation_requested', [])) > 0
    return False

def run_implementation_stage(base_task, tasks, plan, related_files):
    """Run implementation stage with a distinct agent for each task."""
    if not is_stage_requested('implementation'):
        print_stage_header("Implementation Stage Skipped")
        return
        
    print_stage_header("Implementation Stage")
    
    # Get tasks directly from memory instead of using get_memory_value which joins with newlines
    task_list = _global_memory['tasks']
    
    print_task_header(f"Found {len(task_list)} tasks to implement")
    
    for i, task in enumerate(task_list, 1):
        print_task_header(task)
        
        # Create a unique memory instance for this task
        task_memory = MemorySaver()
        
        # Create a fresh agent for each task with its own memory
        task_agent = create_react_agent(model, implementation_tools, checkpointer=task_memory)
        
        # Construct task-specific prompt
        task_prompt = IMPLEMENTATION_PROMPT.format(
            plan=plan,
            key_facts=get_memory_value('key_facts'),
            key_snippets=get_memory_value('key_snippets'),
            task=task,
            related_files="\n".join(related_files),
            base_task=base_task
        )
        
        # Run agent for this task
        while True:
            try:
                for chunk in task_agent.stream(
                    {"messages": [HumanMessage(content=task_prompt)]},
                    {"configurable": {"thread_id": "abc123"}, "recursion_limit": 100}
                ):
                    print_agent_output(chunk)
                break
            except ChatAnthropic.InternalServerError as e:
                print(f"Encountered Anthropic Internal Server Error: {e}. Retrying...")
                continue

def summarize_research_findings(base_task: str, config: dict) -> None:
    """Summarize research findings for informational queries.

    Generates and prints a concise summary of research findings including key facts
    and research notes collected during the research stage.

    Args:
        base_task: The original user query
        config: Configuration dictionary for the agent
    """
    print_stage_header("Research Summary")
    
    # Create dedicated memory for research summarization
    summary_memory = MemorySaver()
    
    # Create fresh agent for summarization with its own memory
    summary_agent = create_react_agent(model, implementation_tools, checkpointer=summary_memory)
    
    summary_prompt = SUMMARY_PROMPT.format(
        base_task=base_task,
        research_notes=get_memory_value('research_notes'),
        key_facts=get_memory_value('key_facts'),
        key_snippets=get_memory_value('key_snippets')
    )
        
    while True:
        try:
            for chunk in summary_agent.stream(
                {"messages": [HumanMessage(content=summary_prompt)]}, 
                config
            ):
                print_agent_output(chunk)
            break
        except ChatAnthropic.InternalServerError as e:
            print(f"Encountered Anthropic Internal Server Error: {e}. Retrying...")
            continue

def run_research_subtasks(base_task: str, config: dict):
    """Run research subtasks with separate agents."""
    subtasks = _global_memory.get('research_subtasks', [])
    if not subtasks:
        return
        
    print_stage_header("Research Subtasks")
    
    # Create tools for subtask agents (excluding spawn_research_subtask and request_implementation)
    subtask_tools = [
        tool for tool in research_tools 
        if tool.name not in ['emit_research_subtask', 'request_implementation']
    ]
    
    for i, subtask in enumerate(subtasks, 1):
        print_task_header(f"Research Subtask {i}/{len(subtasks)}")
        
        # Create fresh memory and agent for each subtask
        subtask_memory = MemorySaver()
        subtask_agent = create_react_agent(
            model,
            subtask_tools,
            checkpointer=subtask_memory
        )
        
        # Run the subtask agent
        subtask_prompt = f"Research Subtask: {subtask}\n\n{RESEARCH_PROMPT}"
        while True:
            try:
                for chunk in subtask_agent.stream(
                    {"messages": [HumanMessage(content=subtask_prompt)]},
                    config
                ):
                    print_agent_output(chunk)
                break
            except ChatAnthropic.InternalServerError as e:
                print(f"Encountered Anthropic Internal Server Error: {e}. Retrying...")
                continue

def validate_environment():
    """Validate required environment variables and dependencies."""
    missing = []
    
    # Check API keys
    if not os.environ.get('ANTHROPIC_API_KEY'):
        missing.append('ANTHROPIC_API_KEY environment variable is not set')
    if not os.environ.get('OPENAI_API_KEY'):
        missing.append('OPENAI_API_KEY environment variable is not set')
    
    # Check for aider binary
    if not shutil.which('aider'):
        missing.append('aider binary not found in PATH. Please install aider: pip install aider')
    
    if missing:
        print("Error: Missing required dependencies:", file=sys.stderr)
        for error in missing:
            print(f"- {error}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point for the ra-aid command line tool."""
    try:
        validate_environment()
        args = parse_arguments()
        base_task = args.message
        config = {
            "configurable": {
                "thread_id": "abc123"
            },
            "recursion_limit": 100,
            "research_only": args.research_only,
            "cowboy_mode": args.cowboy_mode
        }
        
        # Store config in global memory for access by is_informational_query
        _global_memory['config'] = config

        # Run research stage
        print_stage_header("Research Stage")
        research_prompt = f"""User query: {base_task} --keep it simple

{RESEARCH_PROMPT}

Be very thorough in your research and emit lots of snippets, key facts. If you take more than a few steps, be eager to emit research subtasks.{'' if args.research_only else ' Only request implementation if the user explicitly asked for changes to be made.'}"""

        try:
            while True:
                try:
                    for chunk in research_agent.stream(
                        {"messages": [HumanMessage(content=research_prompt)]}, 
                        config
                    ):
                        print_agent_output(chunk)
                    break
                except ChatAnthropic.InternalServerError as e:
                    print(f"Encountered Anthropic Internal Server Error: {e}. Retrying...")
                    continue
        except TaskCompletedException as e:
            print_stage_header("Task Completed")
            raise  # Re-raise to be caught by outer handler

        # Run any research subtasks
        run_research_subtasks(base_task, config)
        
        # For informational queries, summarize findings
        if is_informational_query():
            summarize_research_findings(base_task, config)
        else:
            # Only proceed with planning and implementation if not an informational query
            print_stage_header("Planning Stage")
            planning_prompt = PLANNING_PROMPT.format(
                research_notes=get_memory_value('research_notes'),
                key_facts=get_memory_value('key_facts'),
                key_snippets=get_memory_value('key_snippets'),
                base_task=base_task,
                related_files="\n".join(related_files)
            )

            # Run planning agent
            while True:
                try:
                    for chunk in planning_agent.stream(
                        {"messages": [HumanMessage(content=planning_prompt)]}, 
                        config
                    ):
                        print_agent_output(chunk)
                    break
                except ChatAnthropic.InternalServerError as e:
                    print(f"Encountered Anthropic Internal Server Error: {e}. Retrying...")
                    continue

            # Run implementation stage with task-specific agents
            run_implementation_stage(
                base_task,
                get_memory_value('tasks'),
                get_memory_value('plan'),
                related_files
            )
    except TaskCompletedException:
        sys.exit(0)

if __name__ == "__main__":
    main()
