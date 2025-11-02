from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_host: str
    database_port: int = 5432
    database_name: str
    database_user: str
    database_password: str
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Service Configuration
    service_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def database_url(self) -> str:
        """Construct database URL from individual components."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

