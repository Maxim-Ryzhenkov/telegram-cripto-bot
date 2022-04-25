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

    def __init__(self, message):
        self.message = message.text

        self.amount = None
        self.from_currency = None
        self.to_currency = None
        self.result = None

        self._parse()
        self._get_price()

    def _parse(self):
        """ Распарсить пользовательское сообщение. """
        print(f"Пробую парсить строку {self.message}")
        result = re.match(UserRequest.pattern, self.message)
        try:
            amount, from_currency, to_currency = result.groups()
        except AttributeError:
            raise ValueError("Неправильный формат запроса.\n"
                             "Пример правильного ввода /how_to_convert\n"
                             "Названия валют /all_values")
        print(f"amount={amount}, from_currency={from_currency}, to_currency={to_currency}")
        self.amount = float(amount.replace(",", "."))
        if self.amount <= 0:
            raise ValueError("Сумма должна быть больше нуля.")
        if self.amount > 9999999999:
            raise ValueError("Число суммы не должна превышать 9999999999.")
        self.from_currency = Currency.detect(from_currency)
        self.to_currency = Currency.detect(to_currency)

    def _get_price(self):
        """ Выполнить запрос на сервис через API """
        request_string = f"https://min-api.cryptocompare.com/data/price?fsym={self.from_currency.name}&tsyms={self.to_currency.name}"
        response = requests.get(request_string)
        err_msg = f"К сожалению, у нас технический сбой. Сервис временно недоступен. :("
        if response.status_code != 200:
            raise ApiException(err_msg)
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError:  # если ответ не сериализуется в JSON
            raise ApiException(err_msg)
        result = data.get(self.to_currency.name) * self.amount
        self.result = round(result, 2)
