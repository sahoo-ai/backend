from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from app.core.config import settings
from typing import List, Dict, Optional
import uuid

class MongoDB:
    """MongoDB database manager"""
    
    def __init__(self):
        self.client: MongoClient = MongoClient(settings.MONGODB_URL)
        self.db: Database = self.client.get_database("docuchat")
        self.queries: Collection = self.db.get_collection("queries")
        self.conversations: Collection = self.db.get_collection("conversations")
        
        # Create indexes for better performance
        self.queries.create_index("user_id")
        self.queries.create_index("doc_id")
        self.queries.create_index("timestamp")
        
        print("✅ MongoDB connected")
    
    def save_query(self, query_data: Dict) -> str:
        """
        Save a query to MongoDB
        
        Args:
            query_data: Query information
            
        Returns:
            Query ID
        """
        try:
            if "query_id" not in query_data:
                query_data["query_id"] = str(uuid.uuid4())
            
            result = self.queries.insert_one(query_data)
            return query_data["query_id"]
        except Exception as e:
            print(f"Error saving query: {e}")
            return None
    
    def get_user_queries(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get recent queries for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of queries to return
            
        Returns:
            List of queries
        """
        try:
            queries = self.queries.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            return list(queries)
        except Exception as e:
            print(f"Error getting queries: {e}")
            return []
    
    def get_document_queries(self, doc_id: str, limit: int = 10) -> List[Dict]:
        """
        Get queries related to a specific document
        
        Args:
            doc_id: Document identifier
            limit: Maximum number of queries
            
        Returns:
            List of queries
        """
        try:
            queries = self.queries.find(
                {"doc_id": doc_id}
            ).sort("timestamp", -1).limit(limit)
            
            return list(queries)
        except Exception as e:
            print(f"Error getting document queries: {e}")
            return []
    
    def get_conversation_history(
        self, 
        user_id: str, 
        doc_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get conversation history for context
        
        Args:
            user_id: User identifier
            doc_id: Optional document filter
            limit: Number of recent messages
            
        Returns:
            List of messages in conversation format
        """
        try:
            query = {"user_id": user_id}
            if doc_id:
                query["doc_id"] = doc_id
            
            queries = self.queries.find(query).sort("timestamp", -1).limit(limit)
            
            # Convert to conversation format
            conversation = []
            for q in reversed(list(queries)):
                conversation.append({
                    "role": "user",
                    "content": q.get("question")
                })
                conversation.append({
                    "role": "assistant",
                    "content": q.get("answer")
                })
            
            return conversation
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()

# Global instance
mongodb = MongoDB()