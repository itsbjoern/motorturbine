from .. import errors
from . import base_field


class FloatField(base_field.BaseField):
    def validate_field(self, value):
        if not isinstance(value, float):
            raise errors.TypeMismatch(float, value)

        return True
