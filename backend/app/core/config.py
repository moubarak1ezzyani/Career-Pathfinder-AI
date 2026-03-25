import os
from dotenv import load_dotenv

# Load the .env file if it exists (for local development)
load_dotenv()

# Variables with default values (so GitHub Actions never crashes)
DB_USER = os.getenv("DB_USER_env", "test_user")
DB_PASSWORD = os.getenv("DB_PASSWORD_env", "test_pass")
DB_HOST = os.getenv("DB_HOST_env", "localhost")
DB_PORT = os.getenv("DB_PORT_env", "5432")  # <-- The infamous port that was crashing!
DB_NAME = os.getenv("DB_NAME_env", "test_db")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Security 
SECRET_KEY = os.getenv("SECRET_KEY_env", "default-secret-key-for-tests")
ALGO = os.getenv("ALGO_env", "HS256")
TOKEN_EXPIRE = os.getenv("TOKEN_EXPIRE_env", "30")

# Paths
cv_me_standard = os.getenv("cv_me_standard_env", "dummy.pdf")

# AI models
LLM_MODEL_NAME = "qwen2.5:3b" 
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1")