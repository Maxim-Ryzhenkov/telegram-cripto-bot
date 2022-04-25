import enum


class CommandEnum(enum.Enum):
    @classmethod
    def list(cls) -> list:
        """ Этот метод позволит перечислению использовать оператор 'in'. X in enum.list()."""
        return list(map(lambda c: c.value, cls))


class Command(CommandEnum):
    """ Перечисление команд телеграм бота """
    start = "/start"
    convert = "/convert"
    command_format = "/command_format"
    values = "/values"
    all_values = "/all_values"
