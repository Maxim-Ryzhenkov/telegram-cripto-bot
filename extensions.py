# coding: utf-8

import re
import json
import requests
from currencies import Currency


class ApiException(Exception):
    pass


class UserRequest:
    """
        Класс парсит запрос пользователя,
        проверяет его на ошибки.
        Выполняет запрос к сервису через API
    """
    pattern = r"^\s*([0-9]+[\.|,]?[0-9]*)\s+([a-zA-Zа-яА-Я]+\s*[a-zA-Zа-яА-Я]*)\s+в\s+([a-zA-Zа-яА-Я]+\s*[a-zA-Zа-яА-Я]*)\s*$"

    @staticmethod
    def parse_message(message: str) -> tuple:
        """ Распарсить пользовательское сообщение. """
        print(f"Пробую парсить строку {message}")
        result = re.match(UserRequest.pattern, message)
        try:
            amount, from_currency, to_currency = result.groups()
        except AttributeError:
            raise ValueError("Неправильный формат запроса.\n"
                             "Пример правильного ввода /command_format\n"
                             "Названия валют /all_values")
        print(f"amount={amount}, from_currency={from_currency}, to_currency={to_currency}")
        amount = UserRequest.verify_amount(amount)
        from_currency = Currency.detect(from_currency)
        to_currency = Currency.detect(to_currency)
        return from_currency, to_currency, amount

    @staticmethod
    def verify_amount(value):
        try:
            amount = float(value.replace(",", "."))
        except ValueError:
            raise ValueError("Сумма должна быть числом.")
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля.")
        if amount > 9999999999:
            raise ValueError("Число суммы не должна превышать 9999999999.")
        return amount

    @staticmethod
    def get_price(from_currency: Currency, to_currency: Currency, amount: float) -> float:
        """ Выполнить запрос на сервис через API """
        request_string = f"https://min-api.cryptocompare.com/data/price?fsym={from_currency.name}&tsyms={to_currency.name}"
        response = requests.get(request_string)
        err_msg = f"К сожалению, у нас технический сбой. Сервис временно недоступен. :("
        if response.status_code != 200:
            raise ApiException(err_msg)
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError:  # если ответ не сериализуется в JSON
            raise ApiException(err_msg)
        result = data.get(to_currency.name) * amount
        return round(result, 2)
