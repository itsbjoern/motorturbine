from .. import errors
from . import base_field


class IntField(base_field.BaseField):
    def validate_field(self, value):
        if not isinstance(value, int):
            raise errors.TypeMismatch(int, value)

        return True
