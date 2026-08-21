from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Default path relative to workspace root
    signatures_path: Path = Path("config/signatures.yaml")
    
    # FastAPI configurations
    app_name: str = "AI Asset Discovery Platform"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    model_config = ConfigDict(
        env_prefix="APP_",
        env_file=".env"
    )

settings = Settings()
