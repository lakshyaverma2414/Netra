import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    AGE_GRAPH_NAME = os.getenv("AGE_GRAPH_NAME", "crime_network")
    
    QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "http://127.0.0.1:8081")
    QWEN_MODEL = os.getenv("QWEN_MODEL", "Qwen3-4B-Instruct-2507")

config = Config()
