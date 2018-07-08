from .. import errors, updateset


class BaseField(object):
    """__init__(*, default=None, required=False, unique=False)

    The base class for any field. Used for connecting to the parent document
    and calling general methods for setting and validating values.

    :param default: optional *(None)* –
        Defines a default value based on the field type.
    :param bool required: optional *(False)* –
        Defines if the fields value can be None.
    :param bool unique: optional *(False)* –
        Defines if the fields value has to be unique.

    :raises TypeMismatch: Trying to set a value with the wrong type
    """

    def __init__(
            self, *,
            default=None,
            required=False,
            unique=False,
            sync_enabled=True,
            document=None,
            name=None):
        super().__init__()

        self.document = document
        self.name = name

        self.unique = unique
        self.required = required
        self.sync_enabled = sync_enabled
        self.default = None
        self.updates = []

        if default is not None:
            self.default = default

        # set value directly and use validate_field
        # instead of validate to avoid required check
        self.value = self.default
        if self.value is not None:
            self.validate_field(self.value)

    def clone(self, *args, **kwargs):
        attrs = [
            'unique', 'default', 'required',
            'document', 'name', 'sync_enabled']
        clone_kwargs = {
            name: kwargs.get(name, getattr(self, name))
            for name in attrs
        }
        return self.__class__(*args, **clone_kwargs)

    def synced(self):
        self.updates = []

    def set_value(self, new_value):
        old_val = self.value
        next_operator = updateset.to_operator(self.value, new_value)
        next_operator.set_original_value(old_val)

        new_value = next_operator.apply()
        self.validate(new_value)

        update = {
            'op': next_operator,
            'old_value': old_val
        }
        if isinstance(next_operator, updateset.Set):
            self.updates = [update]
        else:
            self.updates.append(update)

        self.value = new_value

        if self.sync_enabled:
            self.document.update_sync(self.name)

    def get_updates(self, path):
        return self.updates

    def validate(self, value):
        if value is None and not self.required:
            return True

        return self.validate_field(value)

    def __repr__(self):
        return repr(self.value)
