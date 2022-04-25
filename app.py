# coding: utf-8

import telebot

import config
from currencies import Currency
from extensions import UserRequest

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['help', 'start'])
def handler_menu_help(message):
    """ Обработать сообщения, содержащие команды '/start' или '/help'. """
    text = f"Привет, {message.chat.first_name}."
    text = f"{text}\nЯ умею конвертировать одну валюту в другую, по актуальному курсу."
    bot.reply_to(message=message, text=text)
    bot.send_message(chat_id=message.chat.id, text=f"Формат запроса /how_to_convert\n"
                                                   f"Названия основных валют /major_values\n"
                                                   f"Посмотреть полный список валют /all_values")


@bot.message_handler(commands=['all_values', ])
def handler_all_values(message):
    """ Обработчик команды '/all_values' выведет полный список доступных валют. """
    bot.reply_to(message, text=f"Все доступные валюты:\n"
                               f"{Currency.printable_string()}\n"
                               f"...\n"
                               f"Формат запроса /how_to_convert")


@bot.message_handler(commands=['major_values', ])
def handler_major_values(message):
    """ Обработчик команды '/major_values' выведет список основных валют. """
    bot.reply_to(message, text=f"{Currency.printable_string(length=5)}\n"
                               f"...\n"
                               f"Полный список валют /all_values\n"
                               f"Формат запроса /how_to_convert")


@bot.message_handler(commands=['how_to_convert', ])
def handler_major_values(message):
    """ Обработчик команды '/how_to_convert' выведет подсказку по формату конвертации. """
    bot.send_message(message.chat.id, text=f"Формат команды:\n"
                                           f"<сумма> <валюта_1> <в/to> <валюте_2>\n"
                                           f"Примеры:\n"
                                           f"200 USD to RUB\n"
                                           f"5 долларов в рублях\n"
                                           f"10 шведских крон в японские иены\n"
                                           f"- я понимаю человеческий язык :)\n"
                                           f"...\n"
                                           f"Полный список валют /all_values\n")


@bot.message_handler()
def request_handler(message):
    """ Обработчик запроса на конвертацию. """
    user_message = UserRequest(message)
    if not user_message.errors:
        bot.send_message(message.chat.id,
                         text=f"{user_message.amount} "
                              f"{user_message.from_currency.correct_print_name(user_message.amount)} = "
                              f"{user_message.result} "
                              f"{user_message.to_currency.correct_print_name(user_message.result)}")
    else:
        for error in user_message.errors:
            bot.reply_to(message, text=f"{error}")
        bot.send_message(chat_id=message.chat.id, text=f"Формат запроса /how_to_convert\n"
                                                       f"Названия основных валют /major_values\n"
                                                       f"Посмотреть полный список валют /all_values")


bot.polling(none_stop=True)
