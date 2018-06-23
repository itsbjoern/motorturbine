from .. import errors


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

        if default is None and required:
            self.validate(default)
        if default is not None:
            self.default = default

        self.value = self.default
        self.validate(self.value)

    def _connect_document(self, document, name):
        self.document = document
        self.name = name

    def set_value(self, value):
        self.validate(value)
        old_val = self.value
        self.value = value
        if self.sync_enabled:
            self.document.update_sync(self.name, old_val)

    def validate(self, value):
        if value is None and not self.required:
            return True

        return self.validate_field(value)

    def __repr__(self):
        return repr(self.value)
