from pyrogram import Client, filters
from pyrogram.types import Message
from utils.db import get_filter
from utils.buttons import build_keyboard


## code for showing result t global filter to user side

def register_user_filter(app: Client):
    @app.on_message(filters.text & filters.private & ~filters.command("start"))
    async def user_filter_handler(_, message: Message):
        keyword = message.text.strip().lower()
        data = await get_filter(keyword)

        if not data:
            return

        caption = data.get("caption", "")
        media_type = data.get("media_type")
        buttons = build_keyboard(data.get("buttons", []))

        # Send appropriate message based on saved media
        if media_type == "photo":
            await message.reply_photo(photo=data["file_id"], caption=caption, reply_markup=buttons)
        elif media_type == "video":
            await message.reply_video(video=data["file_id"], caption=caption, reply_markup=buttons)
        elif media_type == "document":
            await message.reply_document(document=data["file_id"], caption=caption, reply_markup=buttons)
        elif media_type == "animation":
            await message.reply_animation(animation=data["file_id"], caption=caption, reply_markup=buttons)
        elif media_type == "sticker":
            await message.reply_sticker(sticker=data["file_id"])
        elif media_type == "voice":
            await message.reply_voice(voice=data["file_id"], caption=caption)
        elif media_type == "audio":
            await message.reply_audio(audio=data["file_id"], caption=caption)
        else:
            await message.reply_text(caption, reply_markup=buttons)
