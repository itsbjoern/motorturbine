class BaseException(Exception):
    message = None

    def __init__(self, *values):
        assert self.message is not None, 'Don\'t use BaseExceptions!'
        super().__init__(self.message.format(*values))


class FieldExpected(BaseException):
    """__init__(received)

    Is raised when a Document is created with an attribute
    that is not a :class:`~motorturbine.errors.BaseField`.

    >>> raise FieldExpected(str)
    Expected instance of BaseField, got str!

    :param received:
        The received type
    """
    message = 'Expected instance of BaseField, got {!r}!'


class TypeMismatch(BaseException):
    """__init__(expected, received)

    Is raised when an incorrect type was supplied.

    >>> raise TypeMismatch(int, str)
    Expected instance of int, got str!

    :param expected:
        The expected type.
    :param received:
        The received type
    """
    message = 'Expected instance of {!r}, got {!r}!'


class FieldNotFound(BaseException):
    """__init__(field_name, document)

    Is raised when trying to access a property that isn't present as a field.

    >>> raise FieldNotFound(doc, 'attr')
    Field 'attr' was not found on object \
    <ExampleDocument name='Changed My Name' number=15>.

    :param str field_name:
        Name of the field
    :param BaseDocument document:
        The document that was being accessed.
    """
    message = 'Field {!r} was not found on object {!r}.'


class RetryLimitReached(BaseException):
    """__init__(limit, document)

    Is raised during the synchronisation process if the
    specified retry limit is reached.

    >>> raise RetryLimitReached(10, doc)
    Reached the retry limit (10) while trying to save \
    <ExampleDocument name='Changed My Name' number=15>.

    :param int limit:
        The retry limit
    :param BaseDocument received:
        The document that couldn't be synced
    """
    message = 'Reached the retry limit ({!r}) while trying to save {!r}.'


class ConfigurationMismatch(BaseException):
    message = '<{!r}> is required if <{!r}> is set!'
