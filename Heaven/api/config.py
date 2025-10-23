"""
Configuration management for UrbanFlowAI Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # PostgreSQL Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "urbanflow"
    POSTGRES_USER: str = "urbanflow"
    POSTGRES_PASSWORD: str = "urbanflow123"
    
    # Routing Engines Configuration
    OSRM_URL: str = "http://localhost:5000"
    GRAPHHOPPER_URL: str = "http://localhost:8989"
    
    # API Configuration
    API_TITLE: str = "UrbanFlowAI - The Brain"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Central backend API for intelligent city traffic management"
    LOG_LEVEL: str = "INFO"
    
    # Data Contract Settings
    CONGESTION_THRESHOLD_HIGH: float = 0.7  # Above this, streets are considered highly congested
    CONGESTION_THRESHOLD_MEDIUM: float = 0.4  # Medium congestion
    
    # Emergency Route Settings
    EMERGENCY_SPEED_PENALTY: float = 0.3  # Reduce speed to 30% on congested streets for emergency routing
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def database_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Global settings instance
settings = Settings()

