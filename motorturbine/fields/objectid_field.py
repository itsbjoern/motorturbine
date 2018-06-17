from .. import errors
from . import base_field
import bson


class ObjectIdField(base_field.BaseField):
    def validate_field(self, value):
        if not isinstance(value, bson.ObjectId):
            raise errors.TypeMismatch(bson.ObjectId, value)

        return True
