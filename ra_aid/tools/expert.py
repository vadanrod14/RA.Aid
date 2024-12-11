from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from langchain_openai import ChatOpenAI
from .memory import get_memory_value

console = Console()
model = ChatOpenAI(model_name="o1-preview")

# Keep track of context globally
expert_context = []

@tool("emit_expert_context")
def emit_expert_context(context: str) -> str:
    """Add context for the next expert question.

    This should be highly detailed contents such as entire sections of source code, etc.

    Do not include your question in the additional context.

    Err on the side of adding more context rather than less.

    Expert context will be reset after the ask_expert tool is called.
    
    Args:
        context: The context to add
        
    Returns:
        Confirmation message
    """
    global expert_context
    expert_context.append(context)
    return f"Added context: {context}"

@tool("ask_expert")
def ask_expert(question: str) -> str:
    """Ask a question to an expert AI model.

    Keep your questions specific, but long and detailed.

    You only query the expert when you have a specific question in mind.

    The expert can be extremely useful at logic questions, debugging, and reviewing complex source code, but you must provide all context including source manually.

    Try to phrase your question in a way that it does not expand the scope of our top-level task.

    The expert can be prone to overthinking depending on what and how you ask it.
    
    Args:
        question: The question to ask the expert
        
    Returns:
        The expert's response
    """
    global expert_context
    
    # Build query with context and key facts
    query_parts = []
    
    # Add key facts if they exist
    key_facts = get_memory_value('key_facts')
    if key_facts and len(key_facts) > 0:
        query_parts.append("# Key Facts About This Project")
        query_parts.append(key_facts)
    
    # Add other context if it exists
    if expert_context:
        query_parts.append("\n# Additional Context")
        query_parts.append("\n".join(expert_context))
    
    # Add the question last
    if query_parts:  # If we have context/facts, add a newline before question
        query_parts.append("\n# Question")
    query_parts.append(question)
    
    # Join all parts
    query = "\n".join(query_parts)
    
    # Display the query in a panel before making the call
    console.print(Panel(
        Markdown(query),
        title="🤔 Expert Query",
        border_style="yellow"
    ))
    
    # Clear context after use
    expert_context.clear()
    
    # Get response
    response = model.invoke(query)
    
    # Format and display response
    console.print(Panel(
        Markdown(response.content),
        title="Expert Response",
        border_style="blue"
    ))
    
    return response.content
