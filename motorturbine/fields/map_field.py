from .. import errors, updateset
from . import base_field, string_field
import copy


class DictWrapper(dict):
    def __init__(self, *args, dict_field=None, **kwargs):
        self.dict_field = dict_field
        super().__init__(*args, **kwargs)

    def update(self, values):
        if values is None:
            return

        self.dict_field.validate(values)
        for key, value in values.items():
            self[key] = value

    def __setitem__(self, key, value):
        self.dict_field.validate_key(key)

        field = self.to_field(key, value)
        old_value = dict.get(self, key, None)

        if old_value is not None:
            old_value = old_value.value
        self.dict_field.set_index(key, old_value)
        super().__setitem__(key, field)

    def to_field(self, key, value):
        name = '{}.{}'.format(self.dict_field.name, key)
        new_field = self.dict_field.value_field.clone()
        new_field._connect_document(self.dict_field.document, name)

        old_field = self.get(key, None)
        if old_field is not None:
            new_field.set_value(old_field.value)
            new_field.synced()

            # new_field.operator = old_field.operator
        new_field.set_value(value)
        return new_field

    def __getitem__(self, index):
        item = super().__getitem__(index)
        if hasattr(item, 'value'):
            item = item.value
        return item


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
        self.value = DictWrapper(dict_field=self)

    def _connect_document(self, document, name):
        super()._connect_document(document, name)
        self.value.update(self.default)

    def clone(self):
        return self.__class__(
            self.value_field,
            key_field=self.key_field,
            default=self.default,
            required=self.required,
            sync_enabled=self.sync_enabled)

    def set_index(self, name, value):
        return
        self.operator = updateset.Set(dc)

    def synced(self):
        super().synced()

        for name in self.value:
            field = dict.__getitem__(self.value, name)
            field.synced()

    def set_value(self, new_value):
        old_val = self.value.copy()
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

        self.value.clear()
        self.value.update(new_value)

    def get_operator(self, path):
        split = path.split('.')
        field = dict.get(self.value, split[0])
        return field.get_operator('.'.join(split[1:]))

    def __getattr__(self, attr):
        path_split = attr.split('.')
        field_name = path_split[0]
        if len(path_split) == 1:
            return super().__getattribute__(attr)

        return self.value[path_split[1]]

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
