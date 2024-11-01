# Import necessary libraries
import asyncio
from openai import AsyncOpenAI
from config import Config
from datetime import datetime, timezone
from bs4 import BeautifulSoup

def parse_date(date_str):
    
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.astimezone(timezone.utc)  # Normalize to UTC
    return None


def clean_text(text):
    # Normalize and filter to keep only ASCII characters
    return ''.join(char for char in text if ord(char) < 128)