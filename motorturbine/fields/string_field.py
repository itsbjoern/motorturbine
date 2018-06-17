from .. import errors
from . import base_field


class StringField(base_field.BaseField):
    def validate_field(self, value):
        if not isinstance(value, str):
            raise errors.TypeMismatch(str, value)

        return True
