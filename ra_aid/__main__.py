import sqlite3
import argparse
import glob
import os
import sys
import shutil
from rich.panel import Panel
from rich.console import Console
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
from ra_aid.tools.memory import _global_memory, get_related_files
from ra_aid import print_agent_output, print_stage_header, print_task_header, print_error
from ra_aid.prompts import (
    RESEARCH_PROMPT,
    PLANNING_PROMPT,
    IMPLEMENTATION_PROMPT,
)
from ra_aid.exceptions import TaskCompletedException
import time
from anthropic import APIError, APITimeoutError, RateLimitError, InternalServerError

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

# Create console instance
console = Console()

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

def run_agent_with_retry(agent, prompt: str, config: dict):
    """Run an agent with retry logic for internal server errors.
    
    Args:
        agent: The agent to run
        prompt: The prompt to send to the agent
        config: Configuration dictionary for the agent
        
    Returns:
        None
        
    Raises:
        TaskCompletedException: If the task is completed and should exit
        RuntimeError: If max retries exceeded
    """
    max_retries = 20
    base_delay = 1  # Initial delay in seconds
    
    for attempt in range(max_retries):
        try:
            for chunk in agent.stream(
                {"messages": [HumanMessage(content=prompt)]},
                config
            ):
                print_agent_output(chunk)
            break
        except (InternalServerError, APITimeoutError, RateLimitError, APIError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Max retries ({max_retries}) exceeded. Last error: {str(e)}")
            
            delay = base_delay * (2 ** attempt)  # Exponential backoff
            error_type = e.__class__.__name__
            print_error(f"Encountered {error_type}: {str(e)}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
            continue

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
        run_agent_with_retry(task_agent, task_prompt, {"configurable": {"thread_id": "abc123"}, "recursion_limit": 100})


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
        run_agent_with_retry(subtask_agent, subtask_prompt, config)


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
        error_list = "\n".join(f"- {error}" for error in missing)
        print_error(f"Missing required dependencies:\n\n{error_list}")
        sys.exit(1)


def main():
    """Main entry point for the ra-aid command line tool."""
    try:
        try:
            validate_environment()
            args = parse_arguments()

            # Validate message is provided
            if not args.message:
                print_error("--message is required")
                sys.exit(1)
                
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
                run_agent_with_retry(research_agent, research_prompt, config)
            except TaskCompletedException as e:
                print_stage_header("Task Completed")
                raise  # Re-raise to be caught by outer handler

            # Run any research subtasks
            run_research_subtasks(base_task, config)
            
            # Proceed with planning and implementation if not an informational query
            if not is_informational_query():
                print_stage_header("Planning Stage")
                planning_prompt = PLANNING_PROMPT.format(
                    research_notes=get_memory_value('research_notes'),
                    key_facts=get_memory_value('key_facts'),
                    key_snippets=get_memory_value('key_snippets'),
                    base_task=base_task,
                    related_files="\n".join(get_related_files())
                )

                # Run planning agent
                run_agent_with_retry(planning_agent, planning_prompt, config)

                # Run implementation stage with task-specific agents
                run_implementation_stage(
                    base_task,
                    get_memory_value('tasks'),
                    get_memory_value('plan'),
                    get_related_files()
                )
        except TaskCompletedException:
            sys.exit(0)
    finally:
        pass

if __name__ == "__main__":
    main()
