from langchain_ollama import ChatOllama


def get_llm(model: str = "codestral", temperature: float = 0.1) -> ChatOllama:
    """
    Returns an Ollama LLM client.

    Requires Ollama to be running locally: `ollama serve`
    Pull the model first: `ollama pull codestral`

    Use temperature=0.1 for code generation (deterministic).
    Use temperature=0.3 for requirements/docs (slightly more creative).
    """
    return ChatOllama(model=model, temperature=temperature)
