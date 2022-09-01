class HTTPResponseNot200(Exception):
    """Сервер отвечает с ошибкой."""

    pass


class UnknownStatus(Exception):
    """Неизвестный статус ревью."""

    pass


class EmptyData(Exception):
    """Словарь с данными пустой."""

    pass


class APIProblems(Exception):
    """API Яндекса работает с ошибкой."""

    pass
