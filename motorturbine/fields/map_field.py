from .. import errors
from . import base_field, string_field
import copy


class DictWrapper(dict):
    def __init__(self, *args, dict_field=None, **kwargs):
        object.__setattr__(self, 'dict_field', dict_field)
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        self.dict_field.validate_key(key)
        self.dict_field.validate(value)
        old_value = super().get(key, None)
        super().__setitem__(key, value)
        self.dict_field.update_by_name(key, old_value)


class MapField(base_field.BaseField):
    """__init__(value_field, key_field=StringField(), *, \
    default=None, required=False)

    This field only allows a `dict` type to be set as its value.

    If an entire dict is set instead of singular values each key-value pair in
    the new dict has to match the subfields that were set when initialising
    the field.

    :param BaseField value_field:
        Sets the field type that will be used for the values of the dict.
    :param BaseField key_field: optional (:class:`StringField`) –
        Sets the field type that will be used for the keys of the dict.
    """
    def __init__(
            self,
            value_field,
            key_field=string_field.StringField(),
            *,
            default=None,
            required=False):
        self.key_field = key_field
        self.value_field = value_field
        super().__init__(default=default, required=required)
        self.value = DictWrapper(dict_field=self)

    def update_by_name(self, name, value):
        self.document.update_sync('{}.{}'.format(self.name, name), value)

    def set_value(self, value):
        if not isinstance(value, dict):
            raise errors.TypeMismatch(dict, value)

        for key, item in value.items():
            self.validate_key(key)
            self.validate(item)
        old_val = copy.deepcopy(self.value)
        sync_val = {}
        self.value.clear()
        self.value.update(value)
        self.document.update_sync(name, old_val)

    def __getattr__(self, attr):
        path_split = attr.split('.')
        field_attr = path_split[0]

        if len(path_split) == 1:
            return super().__getattr__(attr)

        return self.value[path_split[1]]

    def validate_field(self, value):
        return self.value_field.validate(value)

    def validate_key(self, value):
        return self.key_field.validate(value)
