from .. import errors
from . import base_field


class FloatField(base_field.BaseField):
    """__init__(*, default=None, required=False)

    This field only allows a `float` type to be set as its value.
    """
    def validate_field(self, value):
        if not isinstance(value, float):
            raise errors.TypeMismatch(float, value)

        return True
