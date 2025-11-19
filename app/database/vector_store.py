import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict
from app.core.config import settings
import uuid

class ChromaVectorStore:
    """Handles ChromaDB operations for vector storage"""
    
    def __init__(self):
        # Initialize ChromaDB client with persistence
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "Document chunks with embeddings"}
        )
    
    def add_documents(self, chunks: List[str], doc_id: str, metadata: Dict = None) -> bool:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of text chunks
            doc_id: Unique document identifier
            metadata: Additional metadata for the document
            
        Returns:
            Boolean indicating success
        """
        try:
            # Create unique IDs for each chunk
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Prepare metadata for each chunk
            metadatas = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                if metadata:
                    chunk_metadata.update(metadata)
                metadatas.append(chunk_metadata)
            
            # Add to ChromaDB
            self.collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            
            return True
            
        except Exception as e:
            print(f"Error adding documents to ChromaDB: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            Dictionary with search results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return {
                "success": True,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete all chunks of a document
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Boolean indicating success
        """
        try:
            # Get all IDs for this document
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False