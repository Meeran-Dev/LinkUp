from pydantic import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    SECRET_KEY= os.getenv("SECRET_KEY")
    ALGORITHM= os.getenv("ALGORITHM")

settings=Settings()