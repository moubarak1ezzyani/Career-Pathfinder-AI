import requests
import os
import sys

# Add backend to sys.path to use existing config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import OLLAMA_URL

def check_ollama():
    print(f"Testing connectivity to Ollama at: {OLLAMA_URL}")
    try:
        # Try to list models
        url = f"{OLLAMA_URL.rstrip('/')}/tags" # OpenAI client might use /v1, but tags is at root
        # If OLLAMA_URL has /v1, we strip it for the tags check
        base_root = OLLAMA_URL.replace("/v1", "").rstrip("/")
        tags_url = f"{base_root}/tags"
        
        print(f"Checking tags at: {tags_url}")
        response = requests.get(tags_url, timeout=5)
        if response.status_code == 200:
            print("✅ Successfully connected to Ollama!")
            print("Available models:", response.json().get("models", []))
        else:
            print(f"❌ Connected but received status {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nPossible solutions:")
        print("1. Ensure Ollama is running on the host.")
        print("2. Set OLLAMA_HOST=0.0.0.0 on your host machine before starting Ollama.")
        print("   (e.g., export OLLAMA_HOST=0.0.0.0 && ollama serve)")
        print("3. Check if your firewall is blocking port 11434.")

if __name__ == "__main__":
    check_ollama()
