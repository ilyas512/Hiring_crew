from crewai import LLM
from .settings import GEMINI_API_KEY, LLM_MODEL

llm = LLM(
    model=LLM_MODEL,
    api_key=GEMINI_API_KEY
)
