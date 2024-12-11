from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def print_stage_header(stage: str) -> None:
    """Print a stage header with green styling and rocket emoji. Content is rendered as Markdown.
    
    Args:
        stage: The stage name to print (supports Markdown formatting)
    """
    console.print(Panel(Markdown(stage), title="🚀 Stage", style="green bold"))

def print_task_header(task: str) -> None:
    """Print a task header with yellow styling and wrench emoji. Content is rendered as Markdown.
    
    Args:
        task: The task text to print (supports Markdown formatting)
    """
    console.print(Panel(Markdown(task), title="🔧 Task", border_style="yellow bold"))
