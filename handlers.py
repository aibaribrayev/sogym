from telebot import types
from config import ANIMALS_DATA, ORDER_DATA
from utils import save_order_to_csv
import re

ADMIN_CHAT_ID = 1128870853


def display_animal_info_handler(call, bot):
    animal = ANIMALS_DATA[call.data]
    if animal["current_jiliks"] >= animal["total_jiliks"]:
        full_message = (
            f"🥩 *{animal['name']}*\n"
            "Толық мөлшер жиналды, малды сойып жіліктеп болған соң сізге хабарласамыз.\n"
            "Егер тапсырыстан бас тарту қажет болса, күннің соңына дейін осы нөмірге хабарласыңыз: +77007700370\n"
            "Жаңадан мал сатылымға шыққанда хабарлаймыз."
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
            f"🥩 *{animal['name']}*\n"
            f"1 жіліктің бағасы шамамен 50,000 KZT\n"
            f"Қазір *{animal['current_jiliks']}* жілік жиналды\n"
            f"Бір *{animal['name']}* толу үшін *{available_jiliks}* жілік қалды\n"
        )

        markup = types.InlineKeyboardMarkup()
        btn_contribute = types.InlineKeyboardButton(
            "Тапсырыс беру", callback_data=f"contribute_{call.data}"
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
            "Толық мөлшер жиналды, малды сойып жіліктеп болған соң тапсырыс берген кісілерге хабарласамыз.\n"
            "Егер тапсырыстан бас тарту қажет болса, күннің соңына дейін осы нөмірге хабарласыңыз: +77007700370\n"
            "Жаңадан мал сатылымға шыққанда хабарлаймыз."
        )
        bot.send_photo(
            call.message.chat.id,
            ANIMALS_DATA[animal_key]["full_image_url"],
            caption=full_message,
            parse_mode="Markdown",
        )
        show_main_menu(call.message.chat.id, bot)
    else:
        msg = bot.send_message(
            call.message.chat.id,
            f"Қанша жілік {ANIMALS_DATA[animal_key]['name']} етін алғыңыз келеді? (1-{ANIMALS_DATA[animal_key]['total_jiliks'] - ANIMALS_DATA[animal_key]['current_jiliks']})",
        )
        bot.register_next_step_handler(msg, ask_confirmation_handler, animal_key, bot)


def ask_confirmation_handler(message, animal_key, bot):
    try:
        jiliks = int(message.text)
        if jiliks <= 0 or jiliks > 12:
            raise ValueError(
                f"Жілік саны 1 мен {ANIMALS_DATA[animal_key]['total_jiliks'] - ANIMALS_DATA[animal_key]['current_jiliks']} арасында болуы керек."
            )

        total_price = jiliks * 50000
        if (
            jiliks + ANIMALS_DATA[animal_key]["current_jiliks"]
            > ANIMALS_DATA[animal_key]["total_jiliks"]
        ):
            markup = types.InlineKeyboardMarkup()
            btn_main_menu = types.InlineKeyboardButton(
                "Бас мәзірге оралу", callback_data="main_menu"
            )
            markup.add(btn_main_menu)
            msg = bot.send_message(
                message.chat.id,
                f"Кешіріңіз, қазір тек {ANIMALS_DATA[animal_key]['total_jiliks'] - ANIMALS_DATA[animal_key]['current_jiliks']} жілік қоса аласыз.",
                reply_markup=markup,
            )
            bot.register_next_step_handler(
                msg, ask_confirmation_handler, animal_key, bot
            )
            return

        ORDER_DATA[message.chat.id] = {
            "animal_key": animal_key,
            "jiliks": jiliks,
            "total_price": total_price,
        }
        markup = types.InlineKeyboardMarkup()
        btn_confirm = types.InlineKeyboardButton(
            "Растау", callback_data=f"confirm_{animal_key}_{jiliks}"
        )
        btn_cancel = types.InlineKeyboardButton("Бас тарту", callback_data="cancel")
        markup.add(btn_confirm, btn_cancel)

        bot.send_message(
            message.chat.id,
            f"Сіз {jiliks} жілік {ANIMALS_DATA[animal_key]['name']} етін алуға тапсырыс бердіңіз. Растайсыз ба?\nЖалпы бағасы: {total_price} KZT",
            reply_markup=markup,
        )
    except ValueError:
        markup = types.InlineKeyboardMarkup()
        btn_main_menu = types.InlineKeyboardButton(
            "Бас мәзірге оралу", callback_data="main_menu"
        )
        markup.add(btn_main_menu)
        msg = bot.send_message(
            message.chat.id,
            f"Жілік санын дұрыс енгізіңіз (1-{ANIMALS_DATA[animal_key]['total_jiliks'] - ANIMALS_DATA[animal_key]['current_jiliks']}) немесе алдыңғы мәзірге қайтыңыз.",
            reply_markup=markup,
        )
        bot.register_next_step_handler(msg, ask_confirmation_handler, animal_key, bot)


def handle_contribution_handler(call, bot):
    try:
        data = call.data.split("_")
        animal_key = data[1]
        jiliks = int(data[2])
        total_price = jiliks * 50000  # Fix the total_price definition here

        ORDER_DATA[call.message.chat.id].update({"confirmed": True})

        msg = bot.send_message(
            call.message.chat.id, "Көп рахмет! \nСіздің есіміңіз кім:"
        )
        bot.register_next_step_handler(
            msg, get_name_handler, animal_key, jiliks, bot, total_price
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Бір жерде қате болды: {str(e)}")
        show_main_menu(call.message.chat.id, bot)


def get_name_handler(message, animal_key, jiliks, bot, total_price):
    ORDER_DATA[message.chat.id]["name"] = message.text
    msg = bot.send_message(message.chat.id, "Сізге қай нөмірге хабарласайық:")
    bot.register_next_step_handler(
        msg, get_phone_handler, animal_key, jiliks, bot, total_price
    )


def get_phone_handler(message, animal_key, jiliks, bot, total_price):
    phone_number = message.text
    if not re.match(r"^\+?\d{10,15}$", phone_number):
        msg = bot.send_message(
            message.chat.id,
            "Телефон нөмірі дұрыс емес. Дұрыс телефон нөмірін енгізу қажет (10-15 сан, '+': белгісімен бастауға болады):",
        )
        bot.register_next_step_handler(
            msg, get_phone_handler, animal_key, jiliks, bot, total_price
        )
    else:
        ORDER_DATA[message.chat.id]["phone"] = phone_number
        msg = bot.send_message(
            message.chat.id,
            "Мекенжайыңызды енгізіңіз (2GIS немесе Google Maps сілтемесі):",
        )
        bot.register_next_step_handler(
            msg, get_address_handler, animal_key, jiliks, bot, total_price
        )


def get_address_handler(message, animal_key, jiliks, bot, total_price):
    try:
        address = message.text
        url_pattern = re.compile(
            r"(https:\/\/2gis\.kz\/geo\/|https:\/\/2gis\.kz\/|https:\/\/go\.2gis\.com\/|https:\/\/maps\.app\.goo\.gl\/|https:\/\/www\.google\.com\/maps\/|https:\/\/goo\.gl\/maps\/|https:\/\/maps\.google\.com\/)",
            re.IGNORECASE,
        )
        if not url_pattern.search(address):
            msg = bot.send_message(
                message.chat.id,
                "Сілтеме дұрыс емес. Дұрыс 2GIS немесе Google Maps сілтемесін енгізіңіз:",
            )
            bot.register_next_step_handler(
                msg, get_address_handler, animal_key, jiliks, bot, total_price
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
                    f"🥩 *{ANIMALS_DATA[animal_key]['name']}*\n"
                    "Толық мөлшер жиналды, малды сойып жіліктеп болған соң сізге хабарласамыз.\n"
                    "Жаңадан мал сатылымға шыққанда хабарлаймыз."
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
                    "Бізге сенім артып тапсырыс бергеніңізге көп рахмет! \n\n"
                    "Қажетті адам саны жиналған соң етті адал сойып, жіліктеп болған соң сізге хабарласамыз.\n\n"
                    f"Қазір *{animal['current_jiliks']}* жілік жиналды\n"
                    f"Бір *{animal['name']}* толу үшін *{available_jiliks}* жілік қалды\n"
                )

                bot.send_photo(
                    message.chat.id,
                    animal["image_url"],
                    caption=animal_info,
                    parse_mode="Markdown",
                )

            send_update_to_all_users(
                animal_key, jiliks, bot, exclude_id=message.chat.id
            )

            show_main_menu(message.chat.id, bot)

            bot.send_message(
                ADMIN_CHAT_ID,
                f"Жаңа тапсырыс қабылданды! {jiliks} жілік {ANIMALS_DATA[animal_key]['name']}.\n"
                f"Жалпы бағасы: {total_price} KZT\n"
                f"Есімі: {ORDER_DATA[message.chat.id]['name']}\n"
                f"Телефон нөмірі: {ORDER_DATA[message.chat.id]['phone']}\n"
                f"Мекенжайы: {ORDER_DATA[message.chat.id]['address']}\n",
            )
    except Exception as e:
        bot.send_message(message.chat.id, f"Бір жерде қате болды: {str(e)}")
        show_main_menu(message.chat.id, bot)


def send_update_to_all_users(animal_key, jiliks, bot, exclude_id=None):
    for chat_id in ORDER_DATA:
        if ORDER_DATA[chat_id]["animal_key"] == animal_key and chat_id != exclude_id:
            bot.send_message(
                chat_id,
                f"Жаңа жілік қосылды! Қазір {ANIMALS_DATA[animal_key]['current_jiliks']} жілік жиналды. Бір {ANIMALS_DATA[animal_key]['name']} толу үшін {ANIMALS_DATA[animal_key]['total_jiliks'] - ANIMALS_DATA[animal_key]['current_jiliks']} жілік қалды.\nДостарыңызға айтыңыз, тез толсын!",
            )


def cancel_contribution_handler(call, bot):
    if call.message.chat.id in ORDER_DATA:
        del ORDER_DATA[call.message.chat.id]
    show_main_menu(call.message.chat.id, bot)


def show_main_menu(chat_id, bot):
    bot.send_message(chat_id, "Бас мәзірге оралу үшін /start командасын басыңыз.")
