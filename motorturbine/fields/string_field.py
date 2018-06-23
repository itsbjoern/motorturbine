from .. import errors
from . import base_field


class StringField(base_field.BaseField):
    """__init__(*, default=None, required=False)

    This field only allows a `str` type to be set as its value.
    """
    def validate_field(self, value):
        if not isinstance(value, str):
            raise errors.TypeMismatch(str, value)

        return True
