from .. import errors
from . import base_field
import copy


class DictWrapper(dict):
    def __init__(self, *args, dict_field=None, **kwargs):
        object.__setattr__(self, 'dict_field', dict_field)
        super().__init__(*args, **kwargs)

    def __setitem__(self, name, value):
        self.dict_field.validate(value)
        old_value = super().get(name, None)
        super().__setitem__(name, value)
        self.dict_field.update_by_name(name, old_value)


class MapField(base_field.BaseField):
    def __init__(self, sub_field, default=None):
        self.sub_field = sub_field
        super().__init__()
        self.value = DictWrapper(dict_field=self)

    def update_by_name(self, name, value):
        self.document.update_sync('{}.{}'.format(self.name, name), value)

    def set_value(self, value):
        if not isinstance(value, dict):
            raise errors.TypeMismatch(dict, value)

        for item in value.values():
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
        return self.sub_field.validate(value)
