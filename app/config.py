import os
from dotenv import load_dotenv

# loading dotenv and exporting it using  settings variable
load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///authentication.db")
    ALGORITHM = os.getenv("ALGORITHM", "RS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
    PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_PATH")
settings = Config()

# if we do not have public or private keys, we return an error
if not os.path.exists(settings.PRIVATE_KEY_PATH) or not os.path.exists(settings.PUBLIC_KEY_PATH):
    raise FileNotFoundError("RSA key files not found. Please ensure the paths are correct.")