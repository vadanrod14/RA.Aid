import subprocess
from typing import List, Optional, Dict, Union, Set
from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.text import Text
from ra_aid.proc.interactive import run_interactive_command
from pydantic import BaseModel, Field
from .memory import get_memory_value
from ra_aid.text.processing import truncate_output

console = Console()

# Keep track of related files globally
related_files: List[str] = []
related_files_set: Set[str] = set()

@tool("emit_related_files")
def emit_related_files(files: List[str]) -> List[str]:
    """Store multiple related files that the programmer tool should work with.
    
    Args:
        files: List of file paths to add
        
    Returns:
        List of confirmation messages for added files
    """
    global related_files, related_files_set
    results = []
    added_files = []
    
    # Process unique files
    for file in set(files):  # Remove duplicates in input
        if file not in related_files_set:
            related_files.append(file)
            related_files_set.add(file)
            added_files.append(file)
            results.append(f"Added related file: {file}")
    
    # Rich output - single consolidated panel
    if added_files:
        files_added_md = '\n'.join(f"- `{file}`" for file in added_files)
        md_content = f"**Files Noted:**\n{files_added_md}"
        console.print(Panel(Markdown(md_content), 
                          title="📁 Related Files Noted", 
                          border_style="green"))
    
    return results

class RunProgrammingTaskInput(BaseModel):
    instructions: str = Field(description="Instructions for the programming task")
    files: Optional[List[str]] = Field(None, description="Optional list of files for Aider to examine")

@tool
def run_programming_task(input: RunProgrammingTaskInput) -> Dict[str, Union[str, int, bool]]:
    """Execute a programming task using Aider.

    Be very detailed in your instructions, but do not write the full code for the programmer, as that's the job of the programmer.

    The programmer can edit multiple files at once and is intelligent.

    If any new files are created, remember to emit them using the emit_related_files tool once this tool completes.

    Additionally, before invoking this tool, make sure all existing related files have been emitted using the emit_related_files tool.
    
    Args:
        instructions: Instructions for the programming task
        files: Optional list of files for Aider to examine. If not provided, uses related_files.
        
    Returns:
        A dictionary containing:
            - output: The command output (stdout + stderr combined)
            - return_code: The process return code (0 typically means success)
            - success: Boolean indicating if the command succeeded
    """
    # Build command
    command = [
        "aider",
        "--sonnet",
        "--yes-always",
        "--no-auto-commits",
        "--dark-mode",
        "--no-suggest-shell-commands",
        "-m"
    ]
    
    command.append(input.instructions)
    
    # Use both input files and related files
    files_to_use = set(related_files)  # Start with related files
    if input.files:  # Add any additional input files
        files_to_use.update(input.files)
    
    if files_to_use:
        command.extend(list(files_to_use))
        
    # Create a pretty display of what we're doing
    task_display = [
        "## Instructions\n",
        f"{input.instructions}\n"
    ]
    
    if files_to_use:
        task_display.extend([
            "\n## Files\n",
            *[f"- `{file}`\n" for file in files_to_use]
        ])
    
    markdown_content = "".join(task_display)
    console.print(Panel(Markdown(markdown_content), title="🤖 Aider Task", border_style="bright_blue"))
        
    try:
        # Run the command interactively
        print()
        output, return_code = run_interactive_command(command)
        print()
        
        # Return structured output
        return {
            "output": truncate_output(output.decode() if output else ""),
            "return_code": return_code,
            "success": return_code == 0
        }
        
    except Exception as e:
        print()
        error_text = Text()
        error_text.append("Error running programming task:\n", style="bold red")
        error_text.append(str(e), style="red")
        console.print(error_text)
        
        return {
            "output": str(e),
            "return_code": 1,
            "success": False
        }

# Export the functions
__all__ = ['run_programming_task', 'emit_related_files']
