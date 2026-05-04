import os
import telebot
from telebot import types
from flask import Flask, request

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID"))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

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
    bot.send_message(
        message.chat.id,
        "👋 Welcome to <b>THE SARCASTIC DOCTOR</b> Official Study Assistant.\n\nChoose an option below:",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['free_materials'])
def free_materials(message):
    bot.send_message(
        message.chat.id,
        "📚 <b>FREE STUDY MATERIALS</b>\n\nJoin our free resource hub here:\nhttps://t.me/+4ZjXcxvlqIZkNTY1"
    )

@bot.message_handler(commands=['paid_courses'])
def paid_courses(message):
    bot.send_message(
        message.chat.id,
        "🎓 <b>PAID LECTURE PACKAGES</b>\n\nContact admin here:\nhttps://t.me/TheSarcasticDoctor"
    )

@bot.message_handler(commands=['help'])
def help_user(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>HOW TO USE THIS BOT</b>\n\nUse menu buttons below for materials, paid packages, support and broken reports."
    )

# =========================
# CONTACT ADMIN
# =========================
@bot.message_handler(commands=['contact_admin'])
def contact_admin(message):
    msg = bot.send_message(message.chat.id, "✉️ Send your message for admin:")
    bot.register_next_step_handler(msg, forward_admin_message)

def forward_admin_message(message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    admin_text = f"""
✉️ <b>NEW ADMIN MESSAGE</b>

👤 User: {username}
🆔 USERID:{message.chat.id}

💬 Message:
{message.text}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Done / User Notified", callback_data=f"done_{message.chat.id}"))

    bot.send_message(ADMIN_GROUP_ID, admin_text, reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Your message has been sent to admin.")

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

🔗 Report:
{message.text}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Done / User Notified", callback_data=f"done_{message.chat.id}"))

    bot.send_message(ADMIN_GROUP_ID, admin_text, reply_markup=markup)
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

    try:
        bot.send_message(uid, "🎉 Your requested lecture / issue has been handled by admin. Please check.")
        bot.answer_callback_query(call.id, "Student notified.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        bot.answer_callback_query(call.id, "Could not notify user.")

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

            bot.send_message(uid, f"📩 <b>ADMIN REPLY</b> ({sender}):\n\n{message.text}")
            bot.reply_to(message, "✅ Reply sent to user.")
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
