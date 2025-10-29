from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import requests

TOKEN = 8041869763:AAHp2urfzpk-NrpXc6HeW6CU9E_L6GSVnCk
WEBHOOK_URL = https://script.google.com/macros/s/AKfycby50wbLo_Tl6C0v-1mKYtBjtawY07sVD6TjHtDWmk6eMclGg-dgijTBJ38hfuaPEmrK/exec

CITY, LAST_NAME, FIRST_NAME, MIDDLE_NAME, CLASS, PHONE, EMAIL, END = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Регистрация"], ["Обратная связь"]]
    await update.message.reply_text("Мастер-класс «Искусственный интеллект в жизни человека»", 
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return CITY

# Пример шага регистрации (остальные аналогично)
async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    context.user_data["city"] = city
    await update.message.reply_text("Введите вашу фамилию:")
    return LAST_NAME

# Завершение и отправка данных
async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = {
        "user_id": update.effective_user.id,
        "last_name": context.user_data.get("last_name"),
        "first_name": context.user_data.get("first_name"),
        "middle_name": context.user_data.get("middle_name"),
        "class_num": context.user_data.get("class_num"),
        "phone": context.user_data.get("phone"),
        "email": context.user_data.get("email"),
        "city": context.user_data.get("city")
    }
    requests.post(WEBHOOK_URL, json=data)
    await update.message.reply_text("Спасибо за регистрацию!")
    return ConversationHandler.END

# Сборка
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
