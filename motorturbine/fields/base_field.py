from .. import errors


class BaseField(object):
    value = None
    default = None
    required = False

    def __init__(self, *, default=None, required=False, sync_enabled=True):
        if default is None and required:
            self.validate(default)

        self.required = required
        self.sync_enabled = sync_enabled
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
