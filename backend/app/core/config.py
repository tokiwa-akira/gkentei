"""
Application configuration management
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Project info
    PROJECT_NAME: str = "G検定対策ツール API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    DB_PATH: str = "./data/problems.db"
    CHROMA_PATH: str = "./data/chroma"
    
    # ML Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL_PATH: str = "./models/llama-3-elyza-jp-8b-q4.gguf"
    TRANSFORMERS_CACHE: str = "./cache"
    
    # Performance
    EMBEDDING_BATCH_SIZE: int = 100
    MAX_SEARCH_RESULTS: int = 50
    
    # Scraping
    SCRAPER_DELAY_MS: int = 1000
    USER_AGENT: str = "G-Kentei-Study-Tool/1.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()