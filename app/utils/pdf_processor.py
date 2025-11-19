import pypdf
from typing import List, Dict
import hashlib

class PDFProcessor:
    """Handles PDF text extraction"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file
        
        Args:
            pdf_file_path: Path to the PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Open the PDF
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Get metadata
                num_pages = len(pdf_reader.pages)
                
                # Extract text from all pages
                text_content = []
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():  # Only add non-empty pages
                        text_content.append({
                            "page_number": page_num + 1,
                            "text": text.strip()
                        })
                
                # Combine all text
                full_text = "\n\n".join([page["text"] for page in text_content])
                
                # Generate document hash (unique identifier)
                doc_hash = hashlib.md5(full_text.encode()).hexdigest()
                
                return {
                    "success": True,
                    "num_pages": num_pages,
                    "pages": text_content,
                    "full_text": full_text,
                    "doc_hash": doc_hash,
                    "message": f"Successfully extracted text from {num_pages} pages"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to process PDF: {str(e)}"
            }
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better context
        
        Args:
            text: The text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence end
            if end < text_length:
                # Find the last period, question mark, or exclamation
                last_break = max(
                    chunk.rfind('. '),
                    chunk.rfind('? '),
                    chunk.rfind('! ')
                )
                if last_break != -1:
                    chunk = chunk[:last_break + 1]
                    end = start + last_break + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks