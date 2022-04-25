# coding: utf-8

import telebot
from telebot import types

import config
from currencies import Currency
from extensions import UserRequest
from extensions import ApiException
from commands import Command

bot = telebot.TeleBot(config.TOKEN)

# Клавиатура со списком валют
keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
for currency in Currency.list():
    keyboard.add(types.KeyboardButton(f"{currency}"))


@bot.message_handler(commands=['start', ])
def handler_menu_help(message: telebot.types.Message):
    """ Обработать сообщения, содержащие команды '/start'. """
    bot.reply_to(message=message, text=f"Привет, {message.chat.first_name}.\nЯ умею конвертировать одну валюту в "
                                       f"другую, по актуальному курсу. Список доступных команд есть в меню.")


@bot.message_handler(commands=['all_values', ])
def handler_all_values(message: telebot.types.Message):
    """ Обработчик команды '/all_values' выведет полный список доступных валют. """
    bot.send_message(message.chat.id, text=f"Все доступные валюты:\n{Currency.printable_string()}")


@bot.message_handler(commands=['values', ])
def handler_major_values(message: telebot.types.Message):
    """ Обработчик команды '/major_values' выведет список основных валют. """
    bot.send_message(message.chat.id, text=f"{Currency.printable_string(length=5)}\n"
                                           f"...\nПолный список валют /all_values")


@bot.message_handler(commands=['command_format', ])
def handler_major_values(message: telebot.types.Message):
    """ Обработчик команды '/how_to_convert' выведет подсказку по формату конвертации. """
    bot.send_message(message.chat.id, text=f"Формат текстовой команды:\n"
                                           f"<сумма> <валюта_1> <в/to> <валюте_2>\n"
                                           f"Например:\n"
                                           f"200 USD в китайский юань\n"
                                           f"5 евро в рублях\n"
                                           f"10 шведских крон в японские иены\n"
                                           f"- я понимаю человеческий язык :)\n"
                                           f"...\n"
                                           f"Полный список валют /all_values\n")


@bot.message_handler(commands=["convert", ])
def convert_handler(message: telebot.types.Message):
    """ Обработчик запускает диалог с пользователем для конвертации валюты. """
    bot.send_message(message.chat.id, text="Выберите валюту, из которой конвертировать.", reply_markup=keyboard)
    bot.register_next_step_handler(message, from_currency_handler)


def from_currency_handler(message: telebot.types.Message):
    """ Запрос валюты из которой конвертируем. """
    if message.text in Command.list():
        # Если вместо клавиатурного события пользователь ткнул в меню и прилетела команда
        bot.send_message(message.chat.id, text=f"Получена команда {message.text.strip('/')}. Действие прервано."
                                               f"Чтобы повторить нажмите /convert")
        return
    try:
        from_currency = message.text.split(",")[1].strip()
    except IndexError:
        # Если вместо выбора на клавиатуре пользователь ввел что-то с базовой клавиатуры.
        bot.send_message(message.chat.id, text=f"Воспользуйтесь клавиатурой валют для выбора.\nКонвертация прервана.\n"
                                               f"Чтобы повторить нажмите /convert\nили выберите что-то другое в меню.")
        return
    bot.send_message(message.chat.id, text="Выберите валюту, в которую конвертировать.", reply_markup=keyboard)
    bot.register_next_step_handler(message, to_currency_handler, from_currency)


def to_currency_handler(message: telebot.types.Message, from_currency):
    """ Запрос валюты в которую конвертируем. """
    if message.text in Command.list():
        # Если вместо клавиатурного события пользователь ткнул в меню и прилетела команда
        bot.send_message(message.chat.id, text=f"Получена команда:\n{message.text.strip('/')}\nКонвертация прервана.\n"
                                               f"Чтобы повторить нажмите /convert\nили выберите что-то другое в меню.")
        return
    try:
        to_currency = message.text.split(",")[1].strip()
    except IndexError:
        # Если вместо выбора на клавиатуре пользователь ввел что-то с базовой клавиатуры.
        bot.send_message(message.chat.id, text=f"Воспользуйтесь клавиатурой валют для выбора.\nКонвертация прервана.\n"
                                               f"Чтобы повторить нажмите /convert\nили выберите что-то другое в меню.")
        return
    bot.send_message(message.chat.id, text=f"Сколько {Currency.detect(from_currency).name_many} "
                                           f"вы хотите конвертировать в {Currency.detect(to_currency).name_to1}?")
    bot.register_next_step_handler(message, amount_handler, from_currency, to_currency)


def amount_handler(message: telebot.types.Message, from_currency, to_currency):
    """ Запрос количества валюты которую нужно конвертировать. """
    if message.text in Command.list():
        # Если вместо клавиатурного события пользователь ткнул в меню и прилетела команда
        bot.send_message(message.chat.id, text=f"Получена команда:\n{message.text.strip('/')}\nКонвертация прервана.\n"
                                               f"Чтобы повторить нажмите /convert\nили выберите что-то другое в меню.")
        return
    try:
        # Если пользователь ввел что-то кроме числа.
        amount = UserRequest.verify_amount(message.text.strip())
    except ValueError as e:
        bot.send_message(message.chat.id, text=f"Ошибка:\n{e}\nКонвертация прервана.\nЧтобы повторить нажмите /convert")
        return
    user_message = f"{amount} {from_currency} в {to_currency}"
    print_out_result(user_message, message.chat.id)


@bot.message_handler(content_types=["text", ])
def request_handler(message: telebot.types.Message):
    """ Обработчик текстового запроса на конвертацию. """
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


bot.polling(none_stop=True)
