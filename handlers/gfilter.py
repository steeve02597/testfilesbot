from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_IDS
from utils.db import save_filter
from utils.buttons import parse_buttons_for_db  # updated parser



## this code is for saving gfilter from admin side



def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def register_gfilter(app: Client):
    @app.on_message(filters.command("gfilter") & filters.private)
    async def gfilter_handler(_, message: Message):
        if not is_admin(message.from_user.id):
            return await message.reply_text("🚫 You are not authorized to use this command.")

        if not message.reply_to_message:
            return await message.reply_text("❗Reply to a message with `/gfilter <keyword>` to save it as a filter.", quote=True)

        if len(message.command) < 2:
            return await message.reply_text("❗Please provide a keyword.\n\nUsage: `/gfilter keyword`", quote=True)

        keyword = message.command[1].lower().strip()
        reply = message.reply_to_message

        caption = reply.caption or reply.text or ""
        media = None

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

        # Extract buttons safely and clean caption
        buttons = []
        if caption and "||" in caption:
            parts = caption.split("||", 1)
            caption = parts[0].strip()
            button_text_block = parts[1].strip()
            button_lines = button_text_block.splitlines()
            buttons = parse_buttons_for_db(button_lines)

        # Save filter to DB
        await save_filter(
            keyword=keyword,
            caption=caption,
            media_type=media,
            message=reply,
            buttons=buttons
        )

        await message.reply_text(f"✅ Global filter added for **{keyword}**.")
