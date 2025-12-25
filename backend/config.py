import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/recruitment_db")
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_BUCKET: str = "resumes"
    
    # Groq AI (Free tier - recommended)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Google AI (Fallback)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Email Configuration (Gmail SMTP - Free)
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")  # Gmail App Password
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

settings = Settings()
