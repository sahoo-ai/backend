import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from openai import OpenAI
from app.core.config import settings

def check_available_models():
    """Check which models work with your API key"""
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )
    
    # List of free models to test
    free_models = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.2-1b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemini-flash-1.5-8b-exp",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "qwen/qwen-2-7b-instruct:free",
    ]
    
    print("Testing available free models...\n")
    print("=" * 60)
    
    working_models = []
    
    for model in free_models:
        try:
            print(f"Testing: {model}...", end=" ")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            print("✅ WORKS")
            working_models.append(model)
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                print("❌ Not available")
            elif "401" in error_msg:
                print("❌ API key issue")
            else:
                print(f"❌ Error: {error_msg[:50]}")
    
    print("=" * 60)
    
    if working_models:
        print(f"\n✅ Found {len(working_models)} working models:")
        for model in working_models:
            print(f"   • {model}")
        print(f"\n📝 Recommended: {working_models[0]}")
        print(f"\nUpdate your .env file with:")
        print(f'OPENROUTER_MODEL={working_models[0]}')
    else:
        print("\n❌ No working free models found")
        print("Check your API key or try paid models")

if __name__ == "__main__":
    check_available_models()