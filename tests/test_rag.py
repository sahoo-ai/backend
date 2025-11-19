import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.core.rag_engine import RAGEngine
from app.core.llm_client import OpenRouterClient

def test_openrouter_connection():
    """Test if OpenRouter API works"""
    print("Testing OpenRouter Connection...")
    
    llm_client = OpenRouterClient()
    success = llm_client.test_connection()
    
    if success:
        print("✅ OpenRouter connection successful!")
        return True
    else:
        print("❌ OpenRouter connection failed - check your API key in .env")
        return False

def test_rag_query():
    """Test RAG with sample data"""
    print("\nTesting RAG Engine...")
    
    rag = RAGEngine()
    
    # Add some test documents first
    print("  Adding test documents...")
    test_chunks = [
        "Python is a high-level programming language created by Guido van Rossum in 1991.",
        "Python is widely used for web development, data science, and automation.",
        "FastAPI is a modern Python web framework for building APIs quickly."
    ]
    
    rag.vector_store.add_documents(
        chunks=test_chunks,
        doc_id="test_python_doc",
        metadata={"source": "test"}
    )
    
    print("✅ Test documents added")
    
    # Test query
    print("  Querying: 'Who created Python?'")
    result = rag.query("Who created Python?", n_results=2)
    
    if result["success"]:
        print("✅ RAG query successful!")
        print(f"\n  Answer: {result['answer']}")
        print(f"  Chunks used: {result['num_chunks_used']}")
        print(f"  Model: {result['model']}")
        return True
    else:
        print(f"❌ RAG query failed: {result.get('message', 'Unknown error')}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Complete RAG System")
    print("=" * 60)
    
    # Test 1: OpenRouter connection
    if not test_openrouter_connection():
        print("\n⚠️  Fix OpenRouter connection before continuing")
        exit(1)
    
    # Test 2: RAG system
    test_rag_query()
    
    print("\n" + "=" * 60)
    print("✅ All RAG tests completed!")
    print("=" * 60)