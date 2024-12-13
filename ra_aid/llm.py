import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

def initialize_llm(provider: str, model_name: str) -> BaseChatModel:
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        return ChatOpenAI(openai_api_key=api_key, model=model_name)
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        return ChatAnthropic(anthropic_api_key=api_key, model=model_name)
    elif provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set.")
        return ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model=model_name
        )
    elif provider == "openai-compatible":
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        if not api_key or not api_base:
            raise ValueError("Both OPENAI_API_KEY and OPENAI_API_BASE environment variables must be set.")
        return ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=api_base,
            model=model_name
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")
