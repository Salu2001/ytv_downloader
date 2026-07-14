import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued."""
    user = update.effective_user
    
    welcome_text = (
        f"👋 Hi {user.first_name}!\n\n"
        "I'm a YouTube downloader bot. Send me a YouTube URL and I'll download it for you!\n\n"
        "📌 *How to use:*\n"
        "1️⃣ Send a YouTube video URL\n"
        "2️⃣ Choose Audio (MP3) or Video (MP4)\n"
        "3️⃣ Download your file!\n\n"
        "📹 Supports single videos and playlists!"
    )

    keyboard = [
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )