from pathlib import Path
from typing import Dict, Optional
import os
import glob
from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel

console = Console()

@tool
def note_tech_debt(
    description: str,
    location: Optional[str] = None
) -> Dict[str, any]:
    """Record a technical debt note for later review.
    
    Creates a markdown file in .ra-aid/tech-debt/ containing the technical debt note.
    
    Args:
        description: Description of the technical debt issue
        location: Optional file/location reference where the tech debt was found
    
    Returns:
        Dict containing:
            - success: Boolean indicating if note was saved
            - note_path: Path to the created note file
            - note_number: Sequential number of the note
    """
    # Ensure base directory exists
    base_dir = Path('.ra-aid/tech-debt')
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Find next note number
    existing_notes = glob.glob(str(base_dir / '*.md'))
    next_num = 1
    if existing_notes:
        numbers = [int(Path(note).stem) for note in existing_notes]
        next_num = max(numbers) + 1
    
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
            title="📝 Tech Debt Note",
            border_style="bright_blue"
        )
    )
    
    return {
        'success': True,
        'note_path': str(note_path),
        'note_number': next_num
    }
