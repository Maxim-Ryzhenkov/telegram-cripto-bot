# coding: utf-8

import telebot

import config
from currencies import Currency
from extensions import UserRequest
from extensions import ApiException

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start', 'menu'])
def handler_menu_help(message: telebot.types.Message):
    """ Обработать сообщения, содержащие команды '/start'. """
    text = f"Привет, {message.chat.first_name}."
    text = f"{text}\nЯ умею конвертировать одну валюту в другую, по актуальному курсу."
    bot.reply_to(message=message, text=text)
    bot.send_message(chat_id=message.chat.id, text=f"Формат запроса /help\n"
                                                   f"Названия основных валют /values\n"
                                                   f"Посмотреть полный список валют /all_values")


@bot.message_handler(commands=['all_values', ])
def handler_all_values(message: telebot.types.Message):
    """ Обработчик команды '/all_values' выведет полный список доступных валют. """
    bot.send_message(message.chat.id, text=f"Все доступные валюты:\n"
                                           f"{Currency.printable_string()}\n"
                                           f"...\n"
                                           f"Формат запроса /help")


@bot.message_handler(commands=['values', ])
def handler_major_values(message: telebot.types.Message):
    """ Обработчик команды '/major_values' выведет список основных валют. """
    bot.reply_to(message, text=f"{Currency.printable_string(length=5)}\n"
                               f"...\n"
                               f"Полный список валют /all_values\n"
                               f"Формат запроса /help")


@bot.message_handler(commands=['help', ])
def handler_major_values(message: telebot.types.Message):
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
def request_handler(message: telebot.types.Message):
    """ Обработчик запроса на конвертацию. """
    print_out_result(message.text, message.chat.id)


def print_out_result(message: str, chat_id):
    """ Распарсить строку и вывести результат или сообщение об ошибке. """
    try:
        from_currency, to_currency, amount = UserRequest.parse_message(message)
        result = UserRequest.get_price(from_currency, to_currency, amount)
    except ValueError as e:
        bot.send_message(chat_id, text=f"{e}")
    except ApiException as e:
        bot.send_message(chat_id, text=f"{e}")
    else:
        bot.send_message(chat_id, text=f"{amount} {from_currency.correct_print_name(amount)} = "
                                       f"{result} {to_currency.correct_print_name(result)}")


@bot.message_handler(commands=["convert", ])
def from_currency_handler(message: telebot.types.Message):
    from_currency = message.text.strip()
    bot.send_message(message.chat.id, text="Выберите валюту, из которой конвертировать.")
    bot.register_next_step_handler(message, to_currency_handler, from_currency)


def to_currency_handler(message: telebot.types.Message, from_currency: str):
    to_currency = message.text.strip()
    bot.send_message(message.chat.id, text="Выберите валюту, в которую конвертировать.")
    bot.register_next_step_handler(message, amount_handler, from_currency, to_currency)


def amount_handler(message: telebot.types.Message, from_currency: str, to_currency: str):
    amount = message.text.strip()
    bot.send_message(message.chat.id, text="Введите сумму для конвертации.")
    user_message = f"{amount} {from_currency} в {to_currency}"
    print_out_result(user_message, message.chat.id)


bot.polling(none_stop=True)
