from .. import errors, updateset
from . import base_field, string_field
import copy


class DictWrapper(dict):
    def __init__(self, *args, dict_field=None, **kwargs):
        object.__setattr__(self, 'dict_field', dict_field)
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        old_value = super().get(key, None)
        value = updateset.to_operator(old_value, value)
        if old_value is not None:
            old_value = old_value.apply()

        value.set_original_value(old_value)
        self.dict_field.validate_key(key)
        print(key)
        print(value.apply())
        self.dict_field.validate_value(value.apply())

        super().__setitem__(key, value)
        self.dict_field.update_by_name(key, old_value)

    def __getitem__(self, key):
        val = super().get(key, None)
        print(val)
        if val is None:
            return None
        return val.apply()


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
            required=False,
            sync_enabled=True):
        self.key_field = key_field
        self.value_field = value_field
        super().__init__(
            default=default, required=required, sync_enabled=sync_enabled)
        self.value = updateset.setval(DictWrapper(dict_field=self))
        # TODO: Default

    def update_by_name(self, name, value):
        self.document.update_sync('{}.{}'.format(self.name, name), value)

    def set_value(self, new_value):
        print(self.name, new_value)
        new_value = self.to_operator(new_value)

        old_val = None
        if self.value is not None:
            old_val = self.value.apply()
        old_val = copy.deepcopy(old_val)

        new_value.set_original_value(old_val)

        applied = new_value.apply()
        self.validate(applied)
        self.value = updateset.setval(DictWrapper(dict_field=self, **applied))
        self.document.update_sync(name, old_val)

    def __getattr__(self, attr):
        path_split = attr.split('.')
        field_name = path_split[0]
        if len(path_split) == 1:
            return super().__getattr__(attr)

        current = self.value.update
        return current[path_split[1]]

    def validate_field(self, value):
        if not isinstance(value, dict):
            raise errors.TypeMismatch(dict, value)

        for key, item in value.items():
            self.validate_key(key)
            self.validate_value(item)

    def validate_value(self, value):
        self.value_field.validate(value)

    def validate_key(self, value):
        self.key_field.validate(value)
