# coding: utf-8

import re
import json
import requests
from currencies import Currency


class UserRequest:
    """
        Класс парсит запрос пользователя,
        проверяет его на ошибки.
        Выполняет запрос к сервису через API
    """
    pattern = r"^\s*([0-9]+\.?[0-9]*)\s+([a-zA-Zа-яА-Я]+\s*[a-zA-Zа-яА-Я]*)\s+в\s+([a-zA-Zа-яА-Я]+\s*[a-zA-Zа-яА-Я]*)\s*$"

    def __init__(self, message):
        self.message = message.text
        self.invalid_message_format = False
        self.errors = []

        self.from_currency_ = None
        self.to_currency_ = None

        self.amount = None
        self.from_currency = None
        self.to_currency = None
        self.result = None

        self._parse()
        if not self.errors:
            self._verify()
            if not self.errors:
                self._get_price()

    def _parse(self):
        """ Распарсить пользовательское сообщение. """
        print(f"Пробую парсить строку {self.message}")
        result = re.match(UserRequest.pattern, self.message)
        if result:
            amount, self.from_currency_, self.to_currency_ = result.groups()
            print(f"amount={amount}, from_currency={self.from_currency_}, to_currency={self.to_currency_}")
            self.amount = int(amount)
            self.from_currency = Currency.detect(self.from_currency_)
            self.to_currency = Currency.detect(self.to_currency_)
        else:
            self.errors.append("Неправильный формат запроса.\n"
                               "Пример правильного ввода /how_to_convert\n"
                               "Названия валют /all_values")
            print(f"Строка не соответствует шаблону: {self.message}")

    def _verify(self):
        """ Проверить сообщение на ошибки. """
        if self.amount <= 0:
            self.errors.append("Сумма должна быть больше нуля.")
        if self.amount > 9999999999:
            self.errors.append("Сумма слишком большая!.")
        if not self.from_currency:
            self.errors.append(f"Не удалось найти '{self.from_currency_}' в списке валют. /all_values")
        if not self.to_currency:
            self.errors.append(f"Не удалось найти '{self.to_currency_}' в списке валют. /all_values")

    def _get_price(self):
        """ Выполнить запрос на сервис через API """
        request_string = f"https://min-api.cryptocompare.com/data/price?fsym={self.from_currency.name}&tsyms={self.to_currency.name}"
        response = requests.get(request_string)
        if response.status_code != 200:
            self.errors.append(f"К сожалению, у нас технический сбой. Сервис временно недоступен. :(")
            return
        try:
            data = json.loads(response.content)
            result = data.get(self.to_currency.name) * self.amount
            self.result = round(result, 2)
        except json.JSONDecodeError:    # если ответ не сериализуется в JSON
            self.errors.append(f"К сожалению, у нас технический сбой. Сервис временно недоступен. :(")
