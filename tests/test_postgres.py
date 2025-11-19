import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.database.postgres import postgres_db
from app.models.document import Document
from datetime import datetime

def test_postgres_connection():
    """Test PostgreSQL connection and table creation"""
    print("Testing PostgreSQL Connection...")
    
    try:
        # Create tables
        postgres_db.create_tables()
        print("✅ Tables created successfully")
        
        # Test insert
        with postgres_db.get_session() as session:
            test_doc = Document(
                id="test_doc_001",
                filename="test.pdf",
                file_path="/test/test.pdf",
                file_size=1024,
                num_pages=5,
                doc_hash="abc123",
                full_text="This is test content",
                num_chunks=3,
                doc_metadata={"source": "test"}
            )
            
            session.add(test_doc)
            session.commit()
            print("✅ Test document inserted")
            
            # Test query
            doc = session.query(Document).filter_by(id="test_doc_001").first()
            if doc:
                print(f"✅ Document retrieved: {doc.filename}")
                print(f"   Pages: {doc.num_pages}, Chunks: {doc.num_chunks}")
            
            # Clean up
            session.delete(doc)
            session.commit()
            print("✅ Test document deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing PostgreSQL Database")
    print("=" * 60)
    
    test_postgres_connection()
    
    print("=" * 60)