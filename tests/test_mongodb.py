import sys
import os
from datetime import datetime

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.database.mongodb import mongodb
from app.models.query import Query

def test_mongodb_connection():
    """Test MongoDB connection and operations"""
    print("Testing MongoDB Connection...")
    
    try:
        # Test save query
        test_query = Query(
            query_id="test_query_001",
            user_id="test_user",
            question="What is Python?",
            answer="Python is a programming language.",
            doc_id="test_doc_001",
            retrieved_chunks=["chunk1", "chunk2"],
            model_used="llama-3.2",
            tokens_used=50
        )
        
        query_id = mongodb.save_query(test_query.to_dict())
        print(f"✅ Query saved with ID: {query_id}")
        
        # Test retrieve queries
        user_queries = mongodb.get_user_queries("test_user", limit=5)
        print(f"✅ Retrieved {len(user_queries)} queries for user")
        
        if user_queries:
            print(f"   First query: {user_queries[0]['question']}")
        
        # Test document queries
        doc_queries = mongodb.get_document_queries("test_doc_001")
        print(f"✅ Retrieved {len(doc_queries)} queries for document")
        
        # Test conversation history
        conversation = mongodb.get_conversation_history("test_user")
        print(f"✅ Retrieved conversation history: {len(conversation)} messages")
        
        # Clean up - delete test data
        mongodb.queries.delete_many({"user_id": "test_user"})
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing MongoDB Database")
    print("=" * 60)
    
    test_mongodb_connection()
    
    print("=" * 60)