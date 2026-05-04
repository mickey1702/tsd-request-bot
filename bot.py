import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID"))

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# stores admin_message_id -> original_user_id
MESSAGE_MAP = {}

# ---------------- START COMMAND ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🔥 Welcome to THE SARCASTIC DOCTOR Support Bot

Send us:
📚 Study Material Requests
💸 Paid Lecture Complaints
🔗 Broken Link Reports
📝 Anonymous Admin Messages

Just type your message and admin will receive it.
"""
    await update.message.reply_text(text)

# ---------------- USER PRIVATE MESSAGE HANDLER ---------------- #

async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return

    user = update.effective_user
    msg = update.message.text

    username = f"@{user.username}" if user.username else "No Username"

    admin_text = f"""
📩 <b>NEW USER REQUEST</b>

👤 Name: {user.full_name}
🔗 Username: {username}
🆔 User ID: <code>{user.id}</code>

💬 Message:
{msg}
"""

    sent = await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=admin_text,
        parse_mode=ParseMode.HTML
    )

    MESSAGE_MAP[sent.message_id] = user.id

    await update.message.reply_text("✅ Your request has been sent to admin panel.")

# ---------------- ADMIN REPLY SYSTEM ---------------- #

async def admin_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id != ADMIN_GROUP_ID:
        return

    if not update.message.reply_to_message:
        return

    if not update.message.text.startswith(".reply"):
        return

    replied_message_id = update.message.reply_to_message.message_id

    if replied_message_id not in MESSAGE_MAP:
        await update.message.reply_text("❌ Cannot detect original user.")
        return

    target_user_id = MESSAGE_MAP[replied_message_id]
    reply_text = update.message.text.replace(".reply", "", 1).strip()

    if not reply_text:
        await update.message.reply_text("❌ Write some reply after .reply")
        return

    await context.bot.send_message(
        chat_id=target_user_id,
        text=f"📬 Admin Reply:\n\n{reply_text}"
    )

    await update.message.reply_text("✅ Reply sent to user.")

# ---------------- TELEGRAM APPLICATION ---------------- #

telegram_app = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_group_reply))

# ---------------- WEBHOOK ROUTE ---------------- #

@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"

@app.route('/')
def home():
    return "TSD BOT RUNNING"

# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(telegram_app.initialize())
    loop.create_task(telegram_app.start())
    app.run(host="0.0.0.0", port=10000)🔗 Username: {username}

📚 Requirement:
<code>{req}</code>
"""

    bot.send_message(ADMIN_GROUP_ID, admin_text, reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Your request has been sent to admin. Please wait for response.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def fulfilled(call):
    uid = int(call.data.split("_")[1])

    try:
        bot.send_message(uid, "🎉 Your requested lecture has been uploaded in the channel/group. Please check latest posts.")
        bot.answer_callback_query(call.id, "Student notified.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        bot.answer_callback_query(call.id, "Could not notify user.")

@app.route('/')
def home():
    return "Bot Running"

def run_bot():
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_web()
