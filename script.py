import telebot

BOT_TOKEN = "7485751066:AAF8QIut4s-vjQ4FZCNmY8b6bAn7RZy8_vY"
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, f"Сіздің chat_id: {message.chat.id}")


bot.infinity_polling()
