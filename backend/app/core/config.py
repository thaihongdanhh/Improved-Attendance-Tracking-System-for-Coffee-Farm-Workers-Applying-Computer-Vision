from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import validator
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Coffee Portal"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8000",
        "http://localhost:5200",
        "http://sarm.n2nai.io:5174",
        "https://sarm.n2nai.io:5174",
        "http://sarm.n2nai.io",
        "https://sarm.n2nai.io",
        "http://kmou.n2nai.io",
        "https://kmou.n2nai.io",
        "http://kmou.n2nai.io:5174",
        "https://kmou.n2nai.io:5174",
        "http://kmou.n2nai.io:5200",
        "https://kmou.n2nai.io:5200",
        "*"  # Allow all origins for testing
    ]
    
    FIREBASE_CONFIG_PATH: str = os.getenv("FIREBASE_CONFIG_PATH", "app/credentials/firebase-admin.json")
    USE_MOCK_FIREBASE: bool = os.getenv("USE_MOCK_FIREBASE", "False").lower() == "true"
    
    ONNX_MODEL_PATH: str = "app/models/face_recognition.onnx"
    INSIGHTFACE_MODEL_PATH: str = "/home/ailab/.insightface/models/buffalo_l"
    YOLO_BEANS_MODEL_PATH: str = "app/models/coffee_beans.pt"
    YOLO_LEAVES_MODEL_PATH: str = "app/models/coffee_leaves.pt"
    
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        case_sensitive = True

settings = Settings()