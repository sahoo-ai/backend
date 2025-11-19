import os
from openai import OpenAI
from app.core.config import settings
from typing import List, Dict

class OpenRouterClient:
    """Handles interactions with OpenRouter API"""
    
    def __init__(self):
        # Initialize OpenAI client pointing to OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.OPENROUTER_MODEL
    
    def generate_response(
        self, 
        query: str, 
        context: str, 
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Generate response using OpenRouter
        
        Args:
            query: User's question
            context: Relevant document chunks
            conversation_history: Previous messages (optional)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Build the system prompt
            system_prompt = """You are a helpful AI assistant that answers questions based on provided documents.

Rules:
1. Answer ONLY based on the context provided
2. If the answer is not in the context, say "I cannot find that information in the uploaded document"
3. Be concise and accurate
4. Quote relevant parts when helpful"""

            # Build the user message with context
            user_message = f"""Context from document:
{context}

Question: {query}

Please answer the question based only on the context above."""

            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current query
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            
            # Extract the answer
            answer = response.choices[0].message.content
            
            return {
                "success": True,
                "answer": answer,
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": f"Error generating response: {str(e)}"
            }
    
    def test_connection(self) -> bool:
        """Test if OpenRouter connection works"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'Hello'"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"OpenRouter connection failed: {e}")
            return False