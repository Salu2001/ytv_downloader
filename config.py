import os

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Download settings
TEMP_DIR = "/tmp/downloads"
os.makedirs(TEMP_DIR, exist_ok=True)

# Max file size (in bytes) - 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024