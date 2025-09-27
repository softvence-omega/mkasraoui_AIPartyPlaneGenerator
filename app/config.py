# app/config.py
import os
from dotenv import load_dotenv
import cloudinary
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Google GenAI client (Gemini)
GENAI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# local directory for generated images
BASE_DIR = os.getcwd()
GENERATED_DIR = os.path.join(BASE_DIR, "generated_cards")
os.makedirs(GENERATED_DIR, exist_ok=True)
