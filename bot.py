import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== ENV VARIABLES (Railway/GitHub) =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# memory (fast)
verified_users = set()
SECRET_TEXT = "এখনো কিছু set করা হয়নি"

# ===== KEYBOARD =====
def start_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📌 Join Channel", url=CHANNEL_LINK),
        InlineKeyboardButton("✅ Verify", callback_data="verify")
    )
    return kb

# ===== CHECK SUB =====
def is_subscriber(uid):
    try:
        m = bot.get_chat_member(CHANNEL_ID, uid)
        return m.status in ("member", "administrator", "creator")
    except:
        return False

# ===== START =====
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    if is_subscriber(uid):
        verified_users.add(uid)
        bot.send_message(message.chat.id, f"<code>{SECRET_TEXT}</code>")
    else:
        bot.send_message(
            message.chat.id,
            "❌ আগে channel join করো, তারপর Verify চাপো",
            reply_markup=start_kb()
        )

# ===== VERIFY BUTTON =====
@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(call):
    uid = call.from_user.id
    if is_subscriber(uid):
        verified_users.add(uid)
        bot.edit_message_text(
            f"<code>{SECRET_TEXT}</code>",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ আগে channel join করো",
            show_alert=True
        )

# ===== ADMIN SET TEXT =====
@bot.message_handler(commands=["set"])
def set_text(message):
    global SECRET_TEXT
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/set", "", 1).strip()
    if not text:
        bot.reply_to(message, "❌ ব্যবহার:\n/set তোমার text")
        return

    SECRET_TEXT = text
    bot.reply_to(message, "✅ Text update হয়েছে")

# ===== BLOCK OTHERS =====
@bot.message_handler(func=lambda m: True)
def block(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "ℹ️ /set দিয়ে text পরিবর্তন করো")
    else:
        bot.reply_to(message, "🔒 Verify করার পর তথ্য দেখা যাবে")

print("Bot running...")
bot.infinity_polling(skip_pending=True)
