from .. import errors
from . import base_field


class IntField(base_field.BaseField):
    """__init__(*, default=None, required=False)

    This field only allows an `int` type to be set as its value.
    """
    def validate_field(self, value):
        if not isinstance(value, int):
            raise errors.TypeMismatch(int, value)

        return True
