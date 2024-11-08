# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SET_TIMER = 600
    # Database connection string
    DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
    
    # Encryption key
    HEX_ENCRYPTION_KEY = os.getenv("HEX_ENCRYPTION_KEY")
    
    # API keys
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    # URLs
    YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"

    # Database collection names
    DATABASE = "KnowGap"
    TOKENS_COLLECTION = "Tokens"
    QUIZZES_COLLECTION = "Quiz Questions"
    STUDENTS_COLLECTION = "Students"
    COURSES_COLLECTION = "Courses"
    CONTEXTS_COLLECTION = "Course Contexts"

    @classmethod
    def check_config(cls):
        """Method to ensure all necessary config variables are set."""
        missing = [
            var for var in [
                "DB_CONNECTION_STRING", "HEX_ENCRYPTION_KEY", 
                "OPENAI_KEY", "YOUTUBE_API_KEY"
            ]
            if not getattr(cls, var)
        ]
        if missing:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

# Run configuration check at startup
Config.check_config()
