import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.utils.pdf_processor import PDFProcessor
from app.database.vector_store import ChromaVectorStore

def test_pdf_processor():
    """Test if PDF processor can chunk text"""
    print("Testing PDF Processor...")
    
    sample_text = "This is a test document. It has multiple sentences. We will chunk this text. Each chunk should be reasonable size."
    
    chunks = PDFProcessor.chunk_text(sample_text, chunk_size=50, overlap=10)
    
    print(f"✅ Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: {chunk[:50]}...")
    
    return True

def test_vector_store():
    """Test if ChromaDB works"""
    print("\nTesting ChromaDB Vector Store...")
    
    vector_store = ChromaVectorStore()
    
    # Add test documents
    test_chunks = [
        "Python is a programming language.",
        "Machine learning is a subset of AI.",
        "Databases store structured data."
    ]
    
    success = vector_store.add_documents(
        chunks=test_chunks,
        doc_id="test_doc_001",
        metadata={"source": "test"}
    )
    
    if success:
        print("✅ Successfully added documents to ChromaDB")
        
        # Test search
        results = vector_store.search("What is Python?", n_results=2)
        if results["success"]:
            print("✅ Search works!")
            print(f"  Found {len(results['results']['documents'][0])} results")
        else:
            print("❌ Search failed")
            return False
    else:
        print("❌ Failed to add documents")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Running Basic Tests")
    print("=" * 50)
    
    test_pdf_processor()
    test_vector_store()
    
    print("\n" + "=" * 50)
    print("✅ All basic tests completed!")
    print("=" * 50)