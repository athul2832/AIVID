import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
GEMINI_API_KEY_BACKUP = os.getenv("GEMINI_API_KEY_BACKUP", "YOUR_GEMINI_API_KEY_BACKUP_HERE")

# Model Configuration - Different models for different tasks
GEMINI_TEXT_MODEL_NAME = os.getenv("GEMINI_TEXT_MODEL_NAME", "models/gemini-2.5-flash")
GEMINI_IMAGE_GENERATION_MODEL_NAME = os.getenv("GEMINI_IMAGE_GENERATION_MODEL_NAME", "models/gemini-2.5-flash-image")
GEMINI_IMAGE_EDITING_MODEL_NAME = os.getenv("GEMINI_IMAGE_EDITING_MODEL_NAME", "models/gemini-2.5-flash-image-preview")

# Directory Configuration
GENERATED_IMAGES_DIR = Path(os.getenv("GENERATED_IMAGES_DIR", "./generated_images")).resolve()
THUMBNAIL_SIZE = (400, 400)
MAX_IMAGE_SIZE = (1024, 1024)