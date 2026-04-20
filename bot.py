import telebot
import sqlite3

TOKEN = "8680233592:AAFSsX5K7eY3h48soknXtiKQrSfFeZVjD80"
ADMIN_ID = 836376839  # твой Telegram ID

bot = telebot.TeleBot(TOKEN)

# 🗄️ СОЗДАЁМ БАЗУ ДАННЫХ
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


# 💾 ФУНКЦИЯ СОХРАНЕНИЯ
def save_story(user_id, username, text):
    cur.execute(
        "INSERT INTO stories (user_id, username, text) VALUES (?, ?, ?)",
        (user_id, username, text)
    )
    conn.commit()


# --- /start ---
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "Привет, балаганец!\n\n"
        "Ты пришёл сюда со своей историей?\n"
        "Замечательно, мы с радостью её прочитаем и, возможно, она попадёт в юбилейный выпуск газеты.\n\n"
        "Но сначала прочитай правила:\n"
        "• Не более 500 символов\n"
        "• У истории должна быть завязка, развитие сюжета, кульминация, концовка\n\n"
        "✍️ Теперь отправь свою историю одним сообщением."
    )

    bot.send_message(message.chat.id, text)


# --- получение истории ---
@bot.message_handler(func=lambda message: True)
def handle_story(message):

    user_id = message.chat.id
    username = message.from_user.username or "no_username"
    text = message.text

    # защита от пустых сообщений
    if not text:
        return

    # ограничение длины
    if len(text) > 500:
        bot.send_message(user_id, "⚠️ История слишком длинная! Максимум 500 символов.")
        return

    # 💾 сохраняем в базу
    save_story(user_id, username, text)

    # 📩 ответ пользователю
    bot.send_message(
        user_id,
        "Спасибо что поделился, твоя история будет прочитана редактором 📖"
    )

    # 📩 уведомление админу
    bot.send_message(
        ADMIN_ID,
        f"📩 НОВАЯ ИСТОРИЯ\n\n"
        f"👤 @{username}\n"
        f"ID: {user_id}\n\n"
        f"📖 {text}"
    )


# --- запуск ---
bot.polling(none_stop=True)