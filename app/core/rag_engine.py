from app.database.vector_store import ChromaVectorStore
from app.core.llm_client import OpenRouterClient
from app.utils.pdf_processor import PDFProcessor
from typing import Dict, List
import os

class RAGEngine:
    """
    Retrieval-Augmented Generation Engine
    Combines vector search with LLM to answer questions
    """
    
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.llm_client = OpenRouterClient()
        self.pdf_processor = PDFProcessor()
    
    def process_and_store_pdf(self, pdf_path: str, doc_id: str, metadata: Dict = None) -> Dict:
        """
        Process PDF and store in vector database
        
        Args:
            pdf_path: Path to PDF file
            doc_id: Unique document identifier
            metadata: Additional metadata
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract text from PDF
            extraction_result = self.pdf_processor.extract_text_from_pdf(pdf_path)
            
            if not extraction_result["success"]:
                return extraction_result
            
            # Chunk the text
            chunks = self.pdf_processor.chunk_text(
                extraction_result["full_text"],
                chunk_size=1000,
                overlap=200
            )
            
            # Add metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "num_pages": extraction_result["num_pages"],
                "doc_hash": extraction_result["doc_hash"],
                "filename": os.path.basename(pdf_path)
            })
            
            # Store in vector database
            success = self.vector_store.add_documents(
                chunks=chunks,
                doc_id=doc_id,
                metadata=metadata
            )
            
            if success:
                return {
                    "success": True,
                    "doc_id": doc_id,
                    "num_chunks": len(chunks),
                    "num_pages": extraction_result["num_pages"],
                    "message": f"Successfully processed and stored {len(chunks)} chunks"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to store document in vector database"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error processing PDF: {str(e)}"
            }
    
    def query(self, question: str, doc_id: str = None, n_results: int = 3) -> Dict:
        """
        Answer a question using RAG
        
        Args:
            question: User's question
            doc_id: Specific document to search (optional)
            n_results: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Step 1: Retrieve relevant chunks from vector store
            search_results = self.vector_store.search(question, n_results=n_results)
            
            if not search_results["success"]:
                return {
                    "success": False,
                    "message": "Failed to search vector database"
                }
            
            # Extract the retrieved documents
            retrieved_docs = search_results["results"]["documents"][0]
            
            if not retrieved_docs:
                return {
                    "success": False,
                    "answer": "No relevant information found in the documents.",
                    "retrieved_chunks": []
                }
            
            # Step 2: Combine retrieved chunks into context
            context = "\n\n---\n\n".join(retrieved_docs)
            
            # Step 3: Generate answer using LLM
            llm_response = self.llm_client.generate_response(
                query=question,
                context=context
            )
            
            if llm_response["success"]:
                return {
                    "success": True,
                    "answer": llm_response["answer"],
                    "retrieved_chunks": retrieved_docs,
                    "num_chunks_used": len(retrieved_docs),
                    "model": llm_response["model"],
                    "tokens_used": llm_response.get("tokens_used")
                }
            else:
                return llm_response
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": f"Error processing query: {str(e)}"
            }