from telebot import types
from config import ANIMALS_DATA, ORDER_DATA
from utils import save_order_to_csv
import re


def display_animal_info_handler(call, bot):
    animal = ANIMALS_DATA[call.data]
    if animal["current_jiliks"] >= animal["total_jiliks"]:
        full_message = (
            f"🐎 *{animal['name']}*\n"
            "The full amount was collected and now the meat is in the process of being prepared and delivered.\n"
            "We will reach out when new animals will be available for sale."
        )
        bot.send_photo(
            call.message.chat.id,
            animal["full_image_url"],
            caption=full_message,
            parse_mode="Markdown",
        )
    else:
        available_jiliks = animal["total_jiliks"] - animal["current_jiliks"]
        animal_info = (
            f" *{animal['name']}*\n"
            f"Price per jilik: 50,000 KZT\n"
            f"Total jiliks: 12\n"
            f"Collected jiliks: {animal['current_jiliks']}\n"
            f"Available jiliks: {available_jiliks}\n"
        )

        markup = types.InlineKeyboardMarkup()
        btn_contribute = types.InlineKeyboardButton(
            "Contribute", callback_data=f"contribute_{call.data}"
        )
        markup.add(btn_contribute)

        bot.send_photo(
            call.message.chat.id,
            animal["image_url"],
            caption=animal_info,
            parse_mode="Markdown",
            reply_markup=markup,
        )


def ask_contribution_handler(call, bot):
    animal_key = call.data.split("_")[1]
    if (
        ANIMALS_DATA[animal_key]["current_jiliks"]
        >= ANIMALS_DATA[animal_key]["total_jiliks"]
    ):
        full_message = (
            f"🥩 *{ANIMALS_DATA[animal_key]['name']}*\n"
            "The full amount was collected and now the meat is in the process of being prepared and delivered.\n"
            "We will reach out when new animals will be available for sale."
        )
        bot.send_photo(
            call.message.chat.id,
            ANIMALS_DATA[animal_key]["full_image_url"],
            caption=full_message,
            parse_mode="Markdown",
        )
    else:
        msg = bot.send_message(
            call.message.chat.id,
            f"How many jiliks would you like to contribute to the {ANIMALS_DATA[animal_key]['name']}? (1-12)",
        )
        bot.register_next_step_handler(msg, ask_confirmation_handler, animal_key, bot)


def ask_confirmation_handler(message, animal_key, bot):
    try:
        jiliks = int(message.text)
        if jiliks <= 0 or jiliks > 12:
            raise ValueError("Jiliks must be between 1 and 12.")

        total_price = jiliks * 50000
        if (
            jiliks + ANIMALS_DATA[animal_key]["current_jiliks"]
            > ANIMALS_DATA[animal_key]["total_jiliks"]
        ):
            bot.reply_to(
                message,
                f"Sorry, you can only contribute up to {ANIMALS_DATA[animal_key]['total_jiliks'] - ANIMALS_DATA[animal_key]['current_jiliks']} jiliks.",
            )
            return

        ORDER_DATA[message.chat.id] = {
            "animal_key": animal_key,
            "jiliks": jiliks,
            "total_price": total_price,
        }
        markup = types.InlineKeyboardMarkup()
        btn_confirm = types.InlineKeyboardButton(
            "Confirm", callback_data=f"confirm_{animal_key}_{jiliks}"
        )
        btn_cancel = types.InlineKeyboardButton("Cancel", callback_data="cancel")
        markup.add(btn_confirm, btn_cancel)

        bot.send_message(
            message.chat.id,
            f"Please confirm your contribution of {jiliks} jiliks to the {ANIMALS_DATA[animal_key]['name']}.\nTotal price: {total_price} KZT",
            reply_markup=markup,
        )
    except ValueError:
        bot.reply_to(message, "Please enter a valid number of jiliks (1-12).")


def handle_contribution_handler(call, bot):
    try:
        data = call.data.split("_")
        animal_key = data[1]
        jiliks = int(data[2])

        ORDER_DATA[call.message.chat.id].update({"confirmed": True})

        msg = bot.send_message(call.message.chat.id, "Please enter your name:")
        bot.register_next_step_handler(msg, get_name_handler, animal_key, jiliks, bot)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"An error occurred: {str(e)}")


def get_name_handler(message, animal_key, jiliks, bot):
    ORDER_DATA[message.chat.id]["name"] = message.text
    msg = bot.send_message(message.chat.id, "Please enter your phone number:")
    bot.register_next_step_handler(msg, get_phone_handler, animal_key, jiliks, bot)


def get_phone_handler(message, animal_key, jiliks, bot):
    phone_number = message.text
    if not re.match(r"^\+?\d{10,15}$", phone_number):
        msg = bot.send_message(
            message.chat.id,
            "Invalid phone number. Please enter a valid phone number (10-15 digits, optionally starting with '+'):",
        )
        bot.register_next_step_handler(msg, get_phone_handler, animal_key, jiliks, bot)
    else:
        ORDER_DATA[message.chat.id]["phone"] = phone_number
        msg = bot.send_message(
            message.chat.id, "Please enter your address (link in 2GIS or Google Maps):"
        )
        bot.register_next_step_handler(
            msg, get_address_handler, animal_key, jiliks, bot
        )


def get_address_handler(message, animal_key, jiliks, bot):
    try:
        address = message.text
        url_pattern = re.compile(
            r"(https:\/\/2gis\.kz\/geo\/|https:\/\/2gis\.kz\/|https:\/\/go\.2gis\.com\/|https:\/\/maps\.app\.goo\.gl\/|https:\/\/www\.google\.com\/maps\/|https:\/\/goo\.gl\/maps\/|https:\/\/maps\.google\.com\/)",
            re.IGNORECASE,
        )
        if not url_pattern.search(address):
            msg = bot.send_message(
                message.chat.id,
                "Invalid address link. Please enter a valid 2GIS or Google Maps link:",
            )
            bot.register_next_step_handler(
                msg, get_address_handler, animal_key, jiliks, bot
            )
        else:
            ORDER_DATA[message.chat.id]["address"] = address
            save_order_to_csv(message.chat.id)

            ANIMALS_DATA[animal_key]["current_jiliks"] += jiliks
            if (
                ANIMALS_DATA[animal_key]["current_jiliks"]
                >= ANIMALS_DATA[animal_key]["total_jiliks"]
            ):
                ANIMALS_DATA[animal_key]["current_jiliks"] = ANIMALS_DATA[animal_key][
                    "total_jiliks"
                ]
                full_message = (
                    f"🐎 *{ANIMALS_DATA[animal_key]['name']}*\n"
                    "The full amount was collected and now the meat is in the process of being prepared and delivered.\n"
                    "We will reach out when new animals will be available for sale."
                )
                bot.send_photo(
                    message.chat.id,
                    ANIMALS_DATA[animal_key]["full_image_url"],
                    caption=full_message,
                    parse_mode="Markdown",
                )
            else:
                animal = ANIMALS_DATA[animal_key]
                available_jiliks = animal["total_jiliks"] - animal["current_jiliks"]
                animal_info = (
                    f"🥩 *{animal['name']}*\n"
                    f"Price per jilik: 50,000 KZT\n"
                    f"Total jiliks: 12\n"
                    f"Collected jiliks: {animal['current_jiliks']}\n"
                    f"Available jiliks: {available_jiliks}\n"
                )

                bot.send_photo(
                    message.chat.id,
                    animal["image_url"],
                    caption=animal_info,
                    parse_mode="Markdown",
                )

            bot.send_message(
                message.chat.id, "Your order has been confirmed and saved."
            )
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")


def cancel_contribution_handler(call, bot):
    if call.message.chat.id in ORDER_DATA:
        del ORDER_DATA[call.message.chat.id]
    bot.send_message(call.message.chat.id, "Contribution cancelled.")
