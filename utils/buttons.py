from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup



## this code is related to saving gfilter buttons from 



def parse_buttons_for_db(lines):
    """Parses custom button text and returns serializable button dicts for DB."""
    keyboard = []
    for line in lines:
        row = []
        parts = line.strip().split("|")
        for part in parts:
            part = part.strip()
            if " - alert:" in part:
                text, alert = part.split(" - alert:", 1)
                row.append({"text": text.strip(), "alert": alert.strip()})
            elif " - " in part:
                text, url = part.split(" - ", 1)
                row.append({"text": text.strip(), "url": url.strip()})
        if row:
            keyboard.append(row)
    return keyboard

def build_keyboard(button_data):
    """Converts button dicts from DB into InlineKeyboardMarkup."""
    keyboard = []
    for row in button_data:
        buttons = []
        for btn in row:
            if "url" in btn:
                buttons.append(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
            elif "alert" in btn:
                buttons.append(InlineKeyboardButton(text=btn["text"], callback_data=f"alert:{btn['alert']}"))
        if buttons:
            keyboard.append(buttons)
    return InlineKeyboardMarkup(keyboard) if keyboard else None
