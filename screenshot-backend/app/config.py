import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Google Cloud Vision API settings
GOOGLE_CLOUD_VISION_CREDENTIALS = os.getenv(
    'GOOGLE_CLOUD_VISION_CREDENTIALS',
    str(BASE_DIR / 'google_vision_credentials.json')
)

# Categories configuration
CATEGORIES = [
    'Work Documents',
    'Code Snippets',
    'Error Messages',
    'Chat Records',
    'Web Screenshots',
    'System Settings',
    'Others'
]

# Category keywords for automatic categorization
CATEGORY_KEYWORDS = {
    'Work Documents': ['document', 'text', 'paper', 'pdf', 'spreadsheet'],
    'Code Snippets': ['code', 'programming', 'computer', 'software', 'development'],
    'Error Messages': ['error', 'warning', 'alert', 'notification', 'message'],
    'Chat Records': ['chat', 'message', 'conversation', 'communication'],
    'Web Screenshots': ['website', 'webpage', 'browser', 'internet'],
    'System Settings': ['settings', 'configuration', 'system', 'preferences'],
    'Others': []
} 