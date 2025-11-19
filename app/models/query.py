from datetime import datetime
from typing import Optional, List, Dict

class Query:
    """Query model for MongoDB"""
    
    def __init__(
        self,
        query_id: str,
        user_id: str,
        question: str,
        answer: str,
        doc_id: Optional[str] = None,
        retrieved_chunks: Optional[List[str]] = None,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
        timestamp: Optional[datetime] = None
    ):
        self.query_id = query_id
        self.user_id = user_id
        self.question = question
        self.answer = answer
        self.doc_id = doc_id
        self.retrieved_chunks = retrieved_chunks or []
        self.model_used = model_used
        self.tokens_used = tokens_used
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for MongoDB"""
        return {
            "query_id": self.query_id,
            "user_id": self.user_id,
            "question": self.question,
            "answer": self.answer,
            "doc_id": self.doc_id,
            "retrieved_chunks": self.retrieved_chunks,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "timestamp": self.timestamp
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Query':
        """Create Query from dictionary"""
        return Query(
            query_id=data.get("query_id"),
            user_id=data.get("user_id"),
            question=data.get("question"),
            answer=data.get("answer"),
            doc_id=data.get("doc_id"),
            retrieved_chunks=data.get("retrieved_chunks", []),
            model_used=data.get("model_used"),
            tokens_used=data.get("tokens_used"),
            timestamp=data.get("timestamp")
        )