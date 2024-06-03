import telebot
from telebot import types
from config import BOT_TOKEN, GENERAL_INFO, GENERAL_INFO_IMAGE_URL
from handlers import (
    display_animal_info_handler,
    ask_contribution_handler,
    handle_contribution_handler,
    cancel_contribution_handler,
)

bot = telebot.TeleBot(BOT_TOKEN)


@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def handle_main_menu(call):
    send_welcome(call.message)


@bot.message_handler(commands=["start", "about"])
def send_welcome(message):
    bot.send_photo(
        message.chat.id,
        GENERAL_INFO_IMAGE_URL,
        caption=GENERAL_INFO,
        parse_mode="Markdown",
    )
    markup = types.InlineKeyboardMarkup()
    btn_siyr = types.InlineKeyboardButton("Сиыр", callback_data="siyr")
    btn_zhylqy = types.InlineKeyboardButton("Жылқы", callback_data="zhylqy")
    markup.add(btn_siyr, btn_zhylqy)

    welcome_message = "Таңдаңыз:"
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["siyr", "zhylqy"])
def display_animal_info(call):
    display_animal_info_handler(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("contribute_"))
def ask_contribution(call):
    ask_contribution_handler(call, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def handle_contribution(call):
    handle_contribution_handler(call, bot)


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel_contribution(call):
    cancel_contribution_handler(call, bot)


bot.infinity_polling()
