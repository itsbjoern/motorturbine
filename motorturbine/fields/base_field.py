from .. import errors


class BaseField(object):
    value = None
    default = None
    required = False

    old_value = None

    def __init__(self, *, default=None, required=False):
        if default is None and required:
            self.validate(default)

        self.required = required
        if default is not None:
            self.default = default
        self.value = self.default

        self.validate(self.value)

    def set_value(self, value):
        self.validate(value)
        self.old_value = self.value
        self.value = value

    def validate(self, value):
        if value is None and not self.required:
            return True

        return self.validate_field(value)

    def did_change(self):
        return self.old_value != self.value

    def synced(self):
        self.old_value = None

    def get_query_value(self, name):
        return {name: self.old_value}, {'$set': {name: self.value}}
