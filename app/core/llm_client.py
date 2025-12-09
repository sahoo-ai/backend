import os
import time
from openai import OpenAI
from app.core.config import settings
from typing import List, Dict

# Free models to try in order of preference
FREE_MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-2-9b-it:free",
    "qwen/qwen-2-7b-instruct:free",
]

class OpenRouterClient:
    """Handles interactions with OpenRouter API"""

    def __init__(self):
        # Initialize OpenAI client pointing to OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.OPENROUTER_MODEL
        self.fallback_models = [m for m in FREE_MODELS if m != self.model]
    
    def _call_model(self, model: str, messages: List[Dict]) -> Dict:
        """Make API call to a specific model"""
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )
        answer = response.choices[0].message.content
        return {
            "success": True,
            "answer": answer,
            "model": model,
            "tokens_used": response.usage.total_tokens if response.usage else None
        }

    def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Generate response using OpenRouter with fallback models

        Args:
            query: User's question
            context: Relevant document chunks
            conversation_history: Previous messages (optional)

        Returns:
            Dictionary with response and metadata
        """
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

        # Try primary model first, then fallbacks
        models_to_try = [self.model] + self.fallback_models
        last_error = None

        for model in models_to_try:
            try:
                print(f"Trying model: {model}")
                result = self._call_model(model, messages)
                print(f"Success with model: {model}")
                return result
            except Exception as e:
                error_str = str(e)
                print(f"Model {model} failed: {error_str}")
                last_error = error_str
                # If rate limited (429), try next model
                if "429" in error_str or "rate" in error_str.lower():
                    time.sleep(0.5)  # Brief pause before trying next
                    continue
                # For other errors, also try next model
                continue

        # All models failed
        return {
            "success": False,
            "error": last_error,
            "answer": f"All models are currently rate-limited. Please try again in a few minutes."
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