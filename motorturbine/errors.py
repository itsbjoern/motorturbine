class BaseException(Exception):
    message = None

    def __init__(self, *values):
        assert self.message is not None, 'Don\'t use BaseExceptions!'
        super().__init__(self.message.format(*values))


class FieldExpected(BaseException):
    message = 'Expected instance of BaseField, got {!r}!'


class TypeMismatch(BaseException):
    message = 'Expected instance of {!r}, got {!r}!'


class ConfigurationMismatch(BaseException):
    message = '<{!r}> is required if <{!r}> is set!'
