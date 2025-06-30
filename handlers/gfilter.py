from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_IDS
from utils.db import save_filter
from utils.buttons import parse_buttons_for_db  # must be working version

# Check if user is admin
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Register /gfilter command
def register_gfilter(app: Client):
    @app.on_message(filters.command("gfilter") & filters.private)
    async def gfilter_handler(_, message: Message):
        if not is_admin(message.from_user.id):
            return await message.reply_text("🚫 You are not authorized to use this command.")

        # Ensure admin replied to a message
        if not message.reply_to_message:
            return await message.reply_text(
                "❗Reply to a message with `/gfilter <keyword>` to save it as a filter.",
                quote=True
            )

        # Ensure keyword is given
        if len(message.command) < 2:
            return await message.reply_text(
                "❗Please provide a keyword.\n\nUsage: `/gfilter keyword`",
                quote=True
            )

        keyword = message.command[1].lower().strip()
        reply = message.reply_to_message

        # Extract caption/text
        caption = reply.caption or reply.text or ""
        media = None

        # Identify media type
        if reply.photo:
            media = "photo"
        elif reply.video:
            media = "video"
        elif reply.document:
            media = "document"
        elif reply.animation:
            media = "animation"
        elif reply.sticker:
            media = "sticker"
        elif reply.voice:
            media = "voice"
        elif reply.audio:
            media = "audio"

        # Extract buttons (from same message text)
        buttons = []
        if message.text and "|" in message.text:
            try:
                buttons = parse_buttons_for_db(message.text.strip().splitlines())
            except Exception as e:
                await message.reply_text(f"⚠️ Failed to parse buttons: {e}")
                return

        # Save to database
        await save_filter(
            keyword=keyword,
            caption=caption,
            media_type=media,
            message=reply,
            buttons=buttons
        )

        await message.reply_text(f"✅ Global filter saved for **{keyword}**.")
