import os
import telebot
from telebot import types
from flask import Flask, request

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID"))

FREE_GROUP_LINK = "https://t.me/+zRsJjUdCCABhMDI1"
PAID_CONTACT = "https://t.me/TheSarcasticDoctor"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# active live support sessions
active_support_users = {}

# =========================
# MAIN MENU
# =========================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📚 Free Study Materials", "🎓 Paid Lecture Packages")
    markup.row("✉️ Contact Admin", "🔗 Report Broken Link")
    markup.row("ℹ️ Help")
    return markup

# =========================
# START + COMMANDS
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id

    if uid in active_support_users:
        bot.send_message(uid, "💬 Support session already active.\nContinue sending messages or type /done to close.")
        return

    bot.send_message(
        uid,
        "👋 Welcome to <b>THE SARCASTIC DOCTOR</b> Official Study Assistant.\n\nChoose an option below:",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['free_materials'])
def free_materials(message):
    bot.send_message(
        message.chat.id,
        f"📚 <b>FREE STUDY MATERIALS</b>\n\nJoin our free resource hub here:\n{FREE_GROUP_LINK}"
    )

@bot.message_handler(commands=['paid_courses'])
def paid_courses(message):
    bot.send_message(
        message.chat.id,
        f"🎓 <b>PAID LECTURE PACKAGES</b>\n\nContact admin here:\n{PAID_CONTACT}"
    )

@bot.message_handler(commands=['help'])
def help_user(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>HOW TO USE THIS BOT</b>\n\nUse menu buttons below for study materials, paid packages, support or broken link reports."
    )

# =========================
# LIVE CONTACT ADMIN SUPPORT
# =========================
@bot.message_handler(commands=['contact_admin'])
def contact_admin(message):
    uid = message.chat.id
    active_support_users[uid] = True

    bot.send_message(
        uid,
        "💬 <b>Support session started.</b>\nNow send your messages continuously here.\nType /done whenever finished."
    )

@bot.message_handler(commands=['done'])
def done_chat(message):
    uid = message.chat.id

    if uid in active_support_users:
        del active_support_users[uid]
        bot.send_message(uid, "🔒 Support session closed.\nPress ✉️ Contact Admin anytime to reopen.")

@bot.message_handler(func=lambda m: m.chat.id in active_support_users and m.text not in ["/start", "/done"])
def forward_live_support(message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    admin_text = f"""
📩 <b>LIVE SUPPORT MESSAGE</b>

👤 User: {username}
🆔 USERID:{message.chat.id}

💬 {message.text}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Done / Close Chat", callback_data=f"done_{message.chat.id}"))

    bot.send_message(ADMIN_GROUP_ID, admin_text, reply_markup=markup)

# =========================
# BROKEN LINK REPORT
# =========================
@bot.message_handler(commands=['broken_link'])
def broken_link(message):
    msg = bot.send_message(message.chat.id, "🔗 Send broken link / screenshot / lecture name:")
    bot.register_next_step_handler(msg, save_broken_report)

def save_broken_report(message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    admin_text = f"""
🚨 <b>BROKEN LINK REPORT</b>

👤 User: {username}
🆔 USERID:{message.chat.id}

🔗 {message.text}
"""

    bot.send_message(ADMIN_GROUP_ID, admin_text)
    bot.send_message(message.chat.id, "✅ Broken link report sent. Thank you.")

# =========================
# MENU BUTTONS
# =========================
@bot.message_handler(func=lambda m: m.text == "📚 Free Study Materials")
def btn1(message):
    free_materials(message)

@bot.message_handler(func=lambda m: m.text == "🎓 Paid Lecture Packages")
def btn2(message):
    paid_courses(message)

@bot.message_handler(func=lambda m: m.text == "✉️ Contact Admin")
def btn3(message):
    contact_admin(message)

@bot.message_handler(func=lambda m: m.text == "🔗 Report Broken Link")
def btn4(message):
    broken_link(message)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def btn5(message):
    help_user(message)

# =========================
# DONE BUTTON CALLBACK
# =========================
@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def fulfilled(call):
    uid = int(call.data.split("_")[1])

    if uid in active_support_users:
        del active_support_users[uid]

    try:
        bot.send_message(uid, "🔒 Admin closed this support session.\nPress ✉️ Contact Admin to start again.")
    except:
        pass

    bot.answer_callback_query(call.id, "Support chat closed.")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# =========================
# ADMIN REPLY RELAY SYSTEM
# =========================
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_GROUP_ID and message.reply_to_message is not None)
def admin_reply_relay(message):
    try:
        replied_text = message.reply_to_message.text

        if "USERID:" in replied_text:
            uid = int(replied_text.split("USERID:")[1].split("\n")[0].strip())
            sender = message.from_user.first_name

            bot.send_message(uid, f"💬 <b>{sender}:</b>\n{message.text}")
            bot.reply_to(message, "✅ Reply delivered.")
    except:
        pass

# =========================
# WEBHOOK RECEIVER
# =========================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "TSD BOT WEBHOOK RUNNING"

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://tsd-request-bot.onrender.com/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
