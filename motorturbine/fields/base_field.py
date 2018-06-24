from .. import errors, updateset


class BaseField(object):
    """__init__(*, default=None, required=False)

    The base class for any field. Used for connecting to the parent document
    and calling general methods for setting and validating values.

    :param default: optional *(None)* –
        Defines a default value based on the field type.
    :param bool required: optional *(False)* –
        Defines if the fields value can be None.

    :raises TypeMismatch: Trying to set a value with the wrong type
    """

    def __init__(self, *, default=None, required=False, sync_enabled=True):
        super().__init__()
        self.required = required
        self.sync_enabled = sync_enabled
        self.default = None
        self.operator = None

        if default is not None:
            self.default = default

        # set value directly and use validate_field
        # instead of validate to avoid required check
        self.value = self.default
        if self.value is not None:
            self.validate_field(self.value)

    def _connect_document(self, document, name):
        self.document = document
        self.name = name

    def clone(self):
        return self.__class__(
            default=self.default,
            required=self.required,
            sync_enabled=self.sync_enabled)

    def synced(self):
        self.operator = None

    def set_value(self, new_value):
        old_val = self.value
        new_operator = self.to_operator(new_value)
        new_operator.set_original_value(old_val)

        same_operator = isinstance(new_operator, self.operator.__class__)
        if self.operator is not None and not same_operator:
            if not isinstance(new_operator, updateset.Set):
                raise Exception(
                    'Cant use multiple UpdateOperators without saving')

        new_value = new_operator.apply()
        self.validate(new_value)
        self.operator = new_operator

        self.value = new_value

        if self.sync_enabled:
            self.document.update_sync(self.name, old_val)

    def to_operator(self, value):
        return updateset.to_operator(self.value, value)

    def get_operator(self, path):
        return self.operator

    def validate(self, value):
        if value is None and not self.required:
            return True

        return self.validate_field(value)

    def __repr__(self):
        return repr(self.value)
