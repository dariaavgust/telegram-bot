import telebot
import sqlite3
from flask import Flask
import threading

TOKEN = "8680233592:AAFSsX5K7eY3h48soknXtiKQrSfFeZVjD80"
ADMIN_ID = 836376839

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# база
conn = sqlite3.connect("stories.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    text TEXT
)
""")
conn.commit()

def save_story(user_id, username, text):
    cur.execute(
        "INSERT INTO stories (user_id, username, text) VALUES (?, ?, ?)",
        (user_id, username, text)
    )
    conn.commit()

# веб (для UptimeRobot)
@app.route('/')
def home():
    return "Bot is alive"

# бот
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "Привет, балаганец! Рады тебя видеть.\n\n"
        "Отправь файл со своей историей"
    )

@bot.message_handler(content_types=['text'])
def handle(message):
    text = message.text
    user_id = message.chat.id
    username = message.from_user.username or "no_username"
    
@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.chat.id
    username = message.from_user.username or "no_username"

    # сообщение пользователю
    bot.send_message(user_id, "Спасибо! Файл отправлен редактору 📎")

    # сообщение тебе (кто отправил)
    bot.send_message(
        ADMIN_ID,
        f"📩 НОВЫЙ ФАЙЛ\n\n👤 @{username}\nID: {user_id}"
    )

    # 🔥 пересылка самого файла
    bot.forward_message(
        ADMIN_ID,
        user_id,
        message.message_id
    )
    if len(text) > 1500:
        bot.send_message(user_id, "Слишком длинная история (до 1500 символов)")
        return

    save_story(user_id, username, text)

    bot.send_message(user_id, "Спасибо! История отправлена 📖")

    bot.send_message(ADMIN_ID,
        f"📩 Новая история\n\n@{username}\n{text}"
    )

def run_bot():
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()
threading.Thread(target=run_bot).start()
