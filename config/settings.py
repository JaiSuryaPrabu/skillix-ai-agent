# Settings for the Skillix AI multi-agent
from pydantic_settings import BaseSettings
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GOOGLE_API_KEY:str
    GEMINI_MODEL_NAME: Literal["gemini-1.5-flash","gemini-2.5-flash-lite"] = "gemini-2.5-flash-lite"
    app_name: str = "Skillix AI"
    
    model_config = {"env_file":".env"}

settings = Settings()