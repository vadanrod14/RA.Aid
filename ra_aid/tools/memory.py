from typing import Dict, List, Any, Union, TypedDict, Optional, Sequence
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from langchain_core.tools import tool

class SnippetInfo(TypedDict):
    """Type definition for source code snippet information"""
    filepath: str
    line_number: int
    snippet: str
    description: Optional[str]

console = Console()

# Global memory store
_global_memory: Dict[str, Union[List[Any], Dict[int, str], Dict[int, SnippetInfo], int]] = {
    'research_notes': [],
    'plans': [],
    'tasks': [],
    'research_subtasks': [],
    'key_facts': {},  # Dict[int, str] - ID to fact mapping
    'key_fact_id_counter': 0,  # Counter for generating unique fact IDs
    'key_snippets': {},  # Dict[int, SnippetInfo] - ID to snippet mapping
    'key_snippet_id_counter': 0,  # Counter for generating unique snippet IDs
    'implementation_requested': [],
    'implementation_skipped': []
}

@tool("emit_research_notes")
def emit_research_notes(notes: str) -> str:
    """Store research notes in global memory.
    
    Args:
        notes: The research notes to store
        
    Returns:
        The stored notes
    """
    _global_memory['research_notes'].append(notes)
    console.print(Panel(Markdown(notes), title="🔍 Research Notes"))
    return notes

@tool("emit_plan")
def emit_plan(plan: str) -> str:
    """Store a plan step in global memory.
    
    Args:
        plan: The plan step to store
        
    Returns:
        The stored plan
    """
    _global_memory['plans'].append(plan)
    console.print(Panel(Markdown(plan), title="📋 Plan"))
    return plan

@tool("emit_task")
def emit_task(task: str) -> str:
    """Store a task in global memory.
    
    Args:
        task: The task to store
        
    Returns:
        The stored task
    """
    _global_memory['tasks'].append(task)
    console.print(Panel(Markdown(task), title="✅ Task"))
    return task

@tool("emit_research_subtask")
def emit_research_subtask(subtask: str) -> str:
    """Spawn a research subtask for deeper investigation of a specific topic.
    
    Only use this when a topic requires dedicated focused research beyond the main task.
    This should be used sparingly for truly complex research needs.
    
    Args:
        subtask: Detailed description of the research subtask
        
    Returns:
        Confirmation message
    """
    _global_memory['research_subtasks'].append(subtask)
    console.print(Panel(Markdown(subtask), title="🔬 Research Subtask"))
    return f"Added research subtask: {subtask}"

@tool("emit_key_fact")
def emit_key_fact(fact: str) -> str:
    """Store a key fact about the project or current task in global memory.

    Key facts are things like:
     - Specific files/functions to look at and what they do
     - Coding conventions
     - Specific external interfaces related to the task
    
    Key facts should be objective and not restating things already specified in our top-level task.

    They are generally things that will not change throughout the duration of our top-level task.
    
    Args:
        fact: The key fact to store
        
    Returns:
        The stored fact
    """
    # Get and increment fact ID
    fact_id = _global_memory['key_fact_id_counter']
    _global_memory['key_fact_id_counter'] += 1
    
    # Store fact with ID
    _global_memory['key_facts'][fact_id] = fact
    
    # Display panel with ID
    console.print(Panel(Markdown(fact), title=f"💡 Key Fact #{fact_id}", border_style="bright_cyan"))
    
    # Return fact with ID
    return f"Stored fact #{fact_id}: {fact}"

@tool("emit_key_facts")
def emit_key_facts(facts: List[str]) -> List[str]:
    """Store multiple key facts about the project or current task in global memory.
    
    Args:
        facts: List of key facts to store
        
    Returns:
        List of stored fact confirmation messages
    """
    results = []
    for fact in facts:
        # Get and increment fact ID
        fact_id = _global_memory['key_fact_id_counter']
        _global_memory['key_fact_id_counter'] += 1
        
        # Store fact with ID
        _global_memory['key_facts'][fact_id] = fact
        
        # Display panel with ID
        console.print(Panel(Markdown(fact), title=f"💡 Key Fact #{fact_id}", border_style="bright_cyan"))
        
        # Add result message
        results.append(f"Stored fact #{fact_id}: {fact}")
        
    return results

@tool("delete_key_fact")
def delete_key_fact(fact_id: int) -> str:
    """Delete a key fact from global memory by its ID.
    
    Args:
        fact_id: The ID of the fact to delete
        
    Returns:
        A message indicating success or failure
    """
    if fact_id not in _global_memory['key_facts']:
        error_msg = f"Error: No fact found with ID #{fact_id}"
        console.print(Panel(Markdown(error_msg), title="❌ Delete Failed", border_style="red"))
        return error_msg
        
    # Delete the fact
    deleted_fact = _global_memory['key_facts'].pop(fact_id)
    success_msg = f"Successfully deleted fact #{fact_id}: {deleted_fact}"
    console.print(Panel(Markdown(success_msg), title="🗑️ Fact Deleted", border_style="green"))
    return success_msg

@tool("delete_key_facts")
def delete_key_facts(fact_ids: List[int]) -> List[str]:
    """Delete multiple key facts from global memory by their IDs.
    Silently skips any IDs that don't exist.
    
    Args:
        fact_ids: List of fact IDs to delete
        
    Returns:
        List of success messages for deleted facts
    """
    results = []
    for fact_id in fact_ids:
        if fact_id in _global_memory['key_facts']:
            # Delete the fact
            deleted_fact = _global_memory['key_facts'].pop(fact_id)
            success_msg = f"Successfully deleted fact #{fact_id}: {deleted_fact}"
            console.print(Panel(Markdown(success_msg), title="🗑️ Fact Deleted", border_style="green"))
            results.append(success_msg)
            
    return results

@tool("request_implementation")
def request_implementation(reason: str) -> str:
    """Request that implementation proceed after research/planning.
    Used to indicate the agent should move to implementation stage.
    
    Args:
        reason: Why implementation should proceed
        
    Returns:
        The stored reason
    """
    _global_memory['implementation_requested'].append(reason)
    console.print(Panel(Markdown(reason), title="🚀 Implementation Requested"))
    return reason


@tool("skip_implementation")
def skip_implementation(reason: str) -> str:
    """Indicate that implementation can be skipped.
    Used when research/planning determines no changes are needed.
    
    Args:
        reason: Why implementation can be skipped
        
    Returns:
        The stored reason
    """
    _global_memory['implementation_skipped'].append(reason)
    console.print(Panel(Markdown(reason), title="⏭️ Implementation Skipped"))
    return reason

@tool("emit_key_snippet")
def emit_key_snippet(filepath: str, line_number: int, snippet: str, description: Optional[str] = None) -> str:
    """Store a key source code snippet in global memory.
    
    Args:
        filepath: Path to the source file
        line_number: Line number where the snippet starts
        snippet: The source code snippet text
        description: Optional description of the snippet's significance
        
    Returns:
        The stored snippet information
    """
    # Get and increment snippet ID
    snippet_id = _global_memory['key_snippet_id_counter']
    _global_memory['key_snippet_id_counter'] += 1
    
    # Store snippet info
    snippet_info: SnippetInfo = {
        'filepath': filepath,
        'line_number': line_number,
        'snippet': snippet,
        'description': description
    }
    _global_memory['key_snippets'][snippet_id] = snippet_info
    
    # Format display text as markdown
    display_text = [
        f"**Source Location**:",
        f"- File: `{filepath}`",
        f"- Line: `{line_number}`",
        "",  # Empty line before code block
        "**Code**:",
        "```python",
        snippet.rstrip(),  # Remove trailing whitespace
        "```"
    ]
    if description:
        display_text.extend(["", "**Description**:", description])
    
    # Display panel
    console.print(Panel(Markdown("\n".join(display_text)), title=f"📝 Key Snippet #{snippet_id}", border_style="bright_cyan"))
    
    return f"Stored snippet #{snippet_id}"

@tool("delete_key_snippet")
def delete_key_snippet(snippet_id: int) -> str:
    """Delete a key snippet from global memory by its ID.
    
    Args:
        snippet_id: The ID of the snippet to delete
        
    Returns:
        A message indicating success or failure
    """
    if snippet_id not in _global_memory['key_snippets']:
        error_msg = f"Error: No snippet found with ID #{snippet_id}"
        console.print(Panel(Markdown(error_msg), title="❌ Delete Failed", border_style="red"))
        return error_msg
        
    # Delete the snippet
    deleted_snippet = _global_memory['key_snippets'].pop(snippet_id)
    success_msg = f"Successfully deleted snippet #{snippet_id} from {deleted_snippet['filepath']}"
    console.print(Panel(Markdown(success_msg), title="🗑️ Snippet Deleted", border_style="green"))
    return success_msg

def get_memory_value(key: str) -> str:
    """Get a value from global memory.
    
    Different memory types return different formats:
    - key_facts: Returns numbered list of facts in format '#ID: fact'
    - key_snippets: Returns formatted snippets with file path, line number and content
    - All other types: Returns newline-separated list of values
    
    Args:
        key: The key to get from memory
        
    Returns:
        String representation of the memory values:
        - For key_facts: '#ID: fact' format, one per line
        - For key_snippets: Formatted snippet blocks
        - For other types: One value per line
    """
    values = _global_memory.get(key, [])
    
    if key == 'key_facts':
        # For empty dict, return empty string
        if not values:
            return ""
        # Sort by ID for consistent output and format as markdown sections
        facts = []
        for k, v in sorted(values.items()):
            facts.extend([
                f"## 🔑 Key Fact #{k}",
                "",  # Empty line for better markdown spacing
                v,
                ""  # Empty line between facts
            ])
        return "\n".join(facts).rstrip()  # Remove trailing newline
    
    if key == 'key_snippets':
        if not values:
            return ""
        # Format each snippet with file info and content using markdown
        snippets = []
        for k, v in sorted(values.items()):
            snippet_text = [
                f"## 📝 Code Snippet #{k}",
                "",  # Empty line for better markdown spacing
                f"**Source Location**:",
                f"- File: `{v['filepath']}`",
                f"- Line: `{v['line_number']}`",
                "",  # Empty line before code block
                "**Code**:",
                "```python",
                v['snippet'].rstrip(),  # Remove trailing whitespace
                "```"
            ]
            if v['description']:
                # Add empty line and description
                snippet_text.extend(["", "**Description**:", v['description']])
            snippets.append("\n".join(snippet_text))
        return "\n\n".join(snippets)
    
    # For other types (lists), join with newlines
    return "\n".join(str(v) for v in values)
