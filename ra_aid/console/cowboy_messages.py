import random

COWBOY_MESSAGES = [
    "Yeeehaw! 🤠",
    "Yippee ki yay motherfucker! 🤠",
    "Saddle up partner! 🤠",
    "This ain't my first rodeo! 🤠",
    "Lock and load, partner! 🤠"
]

def get_cowboy_message() -> str:
    """Randomly select and return a cowboy message.
    
    Returns:
        str: A randomly selected cowboy message
    """
    return random.choice(COWBOY_MESSAGES)
