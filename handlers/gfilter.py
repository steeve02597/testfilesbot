import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_IDS
from utils.db import save_filter
from utils.buttons import parse_buttons_for_db  # must match updated format


# Check if user is admin
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def register_gfilter(app: Client):
    @app.on_message(filters.command("gfilter") & filters.private)
    async def gfilter_handler(_, message: Message):
        if not is_admin(message.from_user.id):
            return await message.reply_text("🚫 You are not authorized to use this command.")

        if not message.reply_to_message:
            return await message.reply_text(
                "❗ Reply to a message with `/gfilter <keyword>` to save it as a filter.",
                quote=True
            )

        if len(message.command) < 2:
            return await message.reply_text(
                "❗ Please provide a keyword.\n\nUsage: `/gfilter keyword`",
                quote=True
            )

        keyword = message.command[1].lower().strip()
        reply = message.reply_to_message

        # Extract caption or text
        caption = reply.caption or reply.text or ""
        media = None

        # Determine media type
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

        # Ask admin for button data
        await message.reply(
            "✅ Almost done!\n\nIf you want to add buttons, send them now in this format:\n\n"
            "`urlbutton - Watch : \"https://example.com\"`\n"
            "`alertbutton - Info : This is an alert!`\n\n"
            "Use `|` to place multiple buttons in the same row like:\n"
            "`urlbutton - A : \"https://a.com\" | alertbutton - B : Alert!`\n\n"
            "Send `skip` to skip adding buttons.",
            quote=True
        )

        buttons = []

        try:
            response: Message = await app.listen(message.chat.id, timeout=60)
            if response.text.lower() != "skip":
                try:
                    buttons = parse_buttons_for_db(response.text.strip().splitlines())
                except Exception as e:
                    return await message.reply_text(f"❗ Failed to parse buttons:\n`{e}`", quote=True)
        except asyncio.TimeoutError:
            await message.reply("⏰ Timeout. No buttons were saved.", quote=True)

        # Save to MongoDB
        await save_filter(
            keyword=keyword,
            caption=caption,
            media_type=media,
            message=reply,
            buttons=buttons
        )

        await message.reply_text(f"✅ Global filter saved for **{keyword}**.")
