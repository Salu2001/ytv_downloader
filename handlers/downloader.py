import os
import re
import logging
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import TEMP_DIR

logger = logging.getLogger(__name__)

def is_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube link."""
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
    return re.match(youtube_regex, url) is not None

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube URLs sent by user."""
    url = update.message.text.strip()

    if not is_youtube_url(url):
        await update.message.reply_text(
            "❌ Please send a valid YouTube URL.\n"
            "Example: https://youtube.com/watch?v=..."
        )
        return

    # Store URL in context
    context.user_data['youtube_url'] = url

    keyboard = [
        [
            InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio"),
            InlineKeyboardButton("📹 Video (MP4)", callback_data="video")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎬 *YouTube URL Detected!*\n\n"
        "Choose download format:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await query.edit_message_text(
            "📖 *Help*\n\n"
            "1. Send me a YouTube URL\n"
            "2. Choose Audio or Video\n"
            "3. Wait for download\n\n"
            "⚠️ Large files may take time to process.",
            parse_mode="Markdown"
        )
        return

    if query.data == "cancel":
        await query.edit_message_text("❌ Download cancelled.")
        return

    # Get the stored URL
    url = context.user_data.get('youtube_url')
    if not url:
        await query.edit_message_text(
            "❌ No URL found. Please send a YouTube URL first."
        )
        return

    format_type = query.data  # 'audio' or 'video'
    await query.edit_message_text(
        f"⏳ Processing your {'audio' if format_type == 'audio' else 'video'} request...\n"
        "This may take a few moments."
    )

    try:
        await download_and_send(update, context, url, format_type)
    except Exception as e:
        logger.error(f"Download error: {e}")
        await query.edit_message_text(
            f"❌ Download failed: {str(e)}\n\n"
            "Please try again with a different video."
        )

async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, format_type: str):
    """Download and send the file to user."""
    query = update.callback_query

    # yt-dlp options
    if format_type == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{TEMP_DIR}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
    else:  # video
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': f'{TEMP_DIR}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

    # Download the file
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

        # Fix file extension for audio
        if format_type == 'audio':
            filename = filename.rsplit('.', 1)[0] + '.mp3'

        # Check if file exists
        if not os.path.exists(filename):
            # Try with .webm or other extensions
            for ext in ['.mp4', '.mkv', '.webm', '.mp3', '.m4a']:
                test_file = filename.rsplit('.', 1)[0] + ext
                if os.path.exists(test_file):
                    filename = test_file
                    break

        # Send the file
        with open(filename, 'rb') as f:
            if format_type == 'audio':
                await context.bot.send_audio(
                    chat_id=update.effective_chat.id,
                    audio=f,
                    title=info.get('title', 'Audio'),
                    performer=info.get('uploader', 'Unknown')
                )
            else:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=f,
                    caption=f"📹 {info.get('title', 'Video')}"
                )

        # Clean up
        try:
            os.remove(filename)
        except:
            pass

        await query.edit_message_text(
            f"✅ Download complete!\n\n"
            f"📌 *{info.get('title', 'File')}*\n"
            f"📤 Sent successfully!",
            parse_mode="Markdown"
        )