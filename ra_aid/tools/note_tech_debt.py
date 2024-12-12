from pathlib import Path
from typing import Dict, Optional, Any
import os
import glob
from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel

# Rich styling constants for tech debt UI
BORDER_STYLE = "bright_blue"
TECH_DEBT_NOTE_EMOJI = "📝"
TECH_DEBT_CLEANUP_EMOJI = "🧹"

MAX_NOTES = 10  # Maximum number of tech debt notes before cleanup warning

console = Console()

@tool
def note_tech_debt(
    description: str,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """Record a technical debt note for later review.
    
    Creates a markdown file in .ra-aid/tech-debt/ containing the technical debt note.
    The system maintains a limit of MAX_NOTES (10) tech debt notes before triggering
    cleanup procedures. When this limit is reached, a cleanup agent is spawned to
    analyze and suggest notes for removal.
    
    Args:
        description: Description of the technical debt issue
        location: Optional file/location reference where the tech debt was found
    
    Returns:
        Dict containing:
            - success: Boolean indicating if note was saved
            - note_path: Path to the created note file
            - note_number: Sequential number of the note
            - cleanup_needed: Boolean indicating if note limit was reached
    """
    # Ensure base directory exists
    base_dir = Path('.ra-aid/tech-debt')
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Find existing notes and determine next note number
    existing_notes = glob.glob(str(base_dir / '*.md'))
    next_num = 1
    cleanup_needed = False
    
    if existing_notes:
        # Extract note numbers from filenames and find highest number
        numbers = [int(Path(note).stem) for note in existing_notes]
        next_num = max(numbers) + 1
        
        # Check if we've hit the note limit that triggers cleanup
        if len(existing_notes) >= MAX_NOTES:
            cleanup_needed = True
            console.print(
                Panel(
                    f"""[bold]Tech Debt Threshold Reached[/bold]

• Current Count: {len(existing_notes)} notes
• Maximum Limit: {MAX_NOTES} notes
• Status: Spawning cleanup/triage agent

[dim italic]The cleanup agent will analyze note contents and suggest which ones to purge.[/dim italic]
""",
                    title=f"{TECH_DEBT_CLEANUP_EMOJI} Tech Debt Cleanup",
                    border_style=BORDER_STYLE
                )
            )
    
    # Create note path
    note_path = base_dir / f'{next_num}.md'
    
    # Format note content
    content = [f'# Technical Debt Note {next_num}\n']
    content.append('## Description\n')
    content.append(f'{description}\n')
    if location:
        content.append('\n## Location\n')
        content.append(f'{location}\n')
    
    # Write note file
    note_path.write_text(''.join(content))
    
    # Display status panel
    console.print(
        Panel(
            f"Created Tech Debt Note #{next_num} at {note_path}",
            title=f"{TECH_DEBT_NOTE_EMOJI} Tech Debt Note",
            border_style=BORDER_STYLE
        )
    )
    
    return {
        'success': True,
        'note_path': str(note_path),
        'note_number': next_num,
        'cleanup_needed': cleanup_needed
    }
