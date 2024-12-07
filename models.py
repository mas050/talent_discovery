from datetime import datetime
from dataclasses import dataclass

@dataclass
class Usage:
    user_id: str
    timestamp: datetime
    operation_type: str  # 'preprocess', 'chunk', 'embedding', 'rerank'
    prompt_tokens: int
    completion_tokens: int
    model: str
    cost: float