import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLOUD_VISION_API_KEY = os.getenv("GOOGLE_CLOUD_VISION_API_KEY")
