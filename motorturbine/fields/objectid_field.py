from .. import errors
from . import base_field
import bson


class ObjectIdField(base_field.BaseField):
    """__init__(*, default=None, required=False)

    This field only allows a :class:`bson.ObjectId` to be set as its value.
    """
    def validate_field(self, value):
        if not isinstance(value, bson.ObjectId):
            raise errors.TypeMismatch(bson.ObjectId, value)

        return True
