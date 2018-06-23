class BaseException(Exception):
    message = None

    def __init__(self, *values):
        assert self.message is not None, 'Don\'t use BaseExceptions!'
        super().__init__(self.message.format(*values))


class FieldExpected(BaseException):
    """__init__(received)

    Is used to raise an exception when a Document is created with an attribute
    that is not a :class:`~motorturbine.errors.BaseField`.

    Output:

    >>> Expected instance of BaseField, got str!

    :param received:
        The received type
    """
    message = 'Expected instance of BaseField, got {!r}!'


class TypeMismatch(BaseException):
    """__init__(expected, received)

    Is used to raise an exception when a incorrect type was supplied.

    Output:

    >>> Expected instance of int, got str!

    :param expected:
        The expected type.
    :param received:
        The received type
    """
    message = 'Expected instance of {!r}, got {!r}!'


class ConfigurationMismatch(BaseException):
    message = '<{!r}> is required if <{!r}> is set!'
