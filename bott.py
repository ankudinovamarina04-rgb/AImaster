import logging
import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
)
from config import TOKEN, WEBHOOK_URL

logging.basicConfig(level=logging.INFO)

# Состояния диалога
MAIN_MENU, REG_CITY, REG_LAST, REG_FIRST, REG_MIDDLE, REG_CLASS, REG_PHONE, REG_EMAIL, \
FB_SCORE, FB_USEFUL, FB_APPLY, FB_TOPICS, FB_INVITE, FB_SOUVENIR = range(14)

CITIES = ["Баган","Искитим","Карасук","Купино","Маслянино","Сузун","Татарск","Тогучин","Чаны","Черепаново"]

# Отправка данных в Google Таблицу
def send_to_sheet(payload: dict, sheet: str):
    try:
        data = {"sheet": sheet, **payload}
        requests.post(WEBHOOK_URL, json=data, timeout=10)
    except Exception as e:
        logging.error(f"Ошибка отправки в Google Script: {e}")

# /start
async def start(update, context):
    keyboard = [["Регистрация"], ["Обратная связь"]]
    await update.message.reply_text(
        "📘 Мастер-класс «Искусственный интеллект в жизни человека»\n\nВыберите действие:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MAIN_MENU

# Главное меню
async def main_menu(update, context):
    choice = update.message.text
    if choice == "Регистрация":
        await update.message.reply_text(
            "Принимаете условия обработки персональных данных?",
            reply_markup=ReplyKeyboardMarkup([["Да"], ["Нет"]], one_time_keyboard=True, resize_keyboard=True)
        )
        return REG_CITY
    elif choice == "Обратная связь":
        await update.message.reply_text("Оцените мастер-класс от 1 до 5:", reply_markup=ReplyKeyboardRemove())
        return FB_SCORE
    else:
        await update.message.reply_text("Пожалуйста, выберите кнопку из меню.")
        return MAIN_MENU

# ======== РЕГИСТРАЦИЯ ========
async def reg_city(update, context):
    if update.message.text != "Да":
        await update.message.reply_text("Регистрация отменена.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    await update.message.reply_text(
        "Выберите населённый пункт:",
        reply_markup=ReplyKeyboardMarkup([[c] for c in CITIES], one_time_keyboard=True, resize_keyboard=True)
    )
    return REG_LAST

async def reg_last(update, context):
    context.user_data["city"] = update.message.text
    await update.message.reply_text("Введите фамилию:", reply_markup=ReplyKeyboardRemove())
    return REG_FIRST

async def reg_first(update, context):
    context.user_data["last_name"] = update.message.text
    await update.message.reply_text("Введите имя:")
    return REG_MIDDLE

async def reg_middle(update, context):
    context.user_data["first_name"] = update.message.text
    await update.message.reply_text("Введите отчество (или '-' если нет):")
    return REG_CLASS

async def reg_class(update, context):
    context.user_data["middle_name"] = update.message.text
    await update.message.reply_text("В каком вы классе? (цифрой):")
    return REG_PHONE

async def reg_phone(update, context):
    context.user_data["class_num"] = update.message.text
    await update.message.reply_text("Введите телефон в формате +7(000)1234567:")
    return REG_EMAIL

async def reg_email(update, context):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Введите электронную почту:")
    return FB_SCORE  # конец регистрации

async def reg_end(update, context):
    context.user_data["email"] = update.message.text
    payload = {
        "user_id": update.effective_user.id,
        "city": context.user_data.get("city"),
        "last_name": context.user_data.get("last_name"),
        "first_name": context.user_data.get("first_name"),
        "middle_name": context.user_data.get("middle_name"),
        "class_num": context.user_data.get("class_num"),
        "phone": context.user_data.get("phone"),
        "email": context.user_data.get("email"),
    }
    send_to_sheet(payload, "Регистрация")
    await update.message.reply_text("✅ Спасибо за регистрацию!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ======== ОБРАТНАЯ СВЯЗЬ ========
async def fb_score(update, context):
    context.user_data["score"] = update.message.text
    await update.message.reply_text(
        "Был ли материал понятным и полезным?",
        reply_markup=ReplyKeyboardMarkup([["Да"], ["Частично"], ["Нет"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return FB_USEFUL

async def fb_useful(update, context):
    context.user_data["useful"] = update.message.text
    await update.message.reply_text(
        "Планируете ли применять полученные знания на практике?",
        reply_markup=ReplyKeyboardMarkup([["Да"], ["Возможно"], ["Нет"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return FB_APPLY

async def fb_apply(update, context):
    context.user_data["apply"] = update.message.text
    await update.message.reply_text("Какие темы вы хотели бы изучить подробнее?")
    return FB_TOPICS

async def fb_topics(update, context):
    context.user_data["topics"] = update.message.text
    await update.message.reply_text(
        "Хотите ли получать приглашения на будущие мастер-классы?",
        reply_markup=ReplyKeyboardMarkup([["Да"], ["Нет"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return FB_INVITE

async def fb_invite(update, context):
    context.user_data["invite"] = update.message.text
    await update.message.reply_text(
        "Вы получили сувенирную продукцию (блокнот, ручка, пакет)?",
        reply_markup=ReplyKeyboardMarkup([["Да"], ["Нет"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return FB_SOUVENIR

async def fb_souvenir(update, context):
    context.user_data["souvenir"] = update.message.text
    payload = {
        "user_id": update.effective_user.id,
        "score": context.user_data.get("score"),
        "useful": context.user_data.get("useful"),
        "apply": context.user_data.get("apply"),
        "topics": context.user_data.get("topics"),
        "invite": context.user_data.get("invite"),
        "souvenir": context.user_data.get("souvenir"),
    }
    send_to_sheet(payload, "Обратная связь")
    await update.message.reply_text("Спасибо за обратную связь!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Команда /cancel
async def cancel(update, context):
    await update.message.reply_text("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            REG_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_city)],
            REG_LAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_last)],
            REG_FIRST: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_first)],
            REG_MIDDLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_middle)],
            REG_CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_class)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_phone)],
            REG_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_email)],
            FB_SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, fb_score)],
            FB_USEFUL: [MessageHandler(filters.TEXT & ~filters.COMMAND, fb_useful)],
            FB_APPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, fb_apply)],
            FB_TOPICS: [MessageHandler(filters.TEXT & ~filters.COMMAND, fb_topics)],
            FB_INVITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, fb_invite)],
            FB_SOUVENIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, fb_souvenir)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("Бот запущен. Отправьте /start в Telegram.")
    app.run_polling()

if __name__ == "__main__":
    main()
