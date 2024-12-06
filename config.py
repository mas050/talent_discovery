# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    GEMINI_API_KEY: str = "YOUR_API_KEY"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    LLM_MODEL: str = "gemini-1.5-flash"
    TOP_K_RESULTS: int = 20
