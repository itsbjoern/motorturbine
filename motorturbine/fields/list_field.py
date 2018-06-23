from .. import errors
from . import base_field
import copy


class ListWrapper(list):
    def __init__(self, *args, list_field=None, **kwargs):
        object.__setattr__(self, 'list_field', list_field)
        super().__init__(*args, **kwargs)

    def __setitem__(self, index, value):
        self.list_field.validate(value)
        old_value = super().__getitem__(index)
        super().__setitem__(index, value)
        self.list_field.update_by_index(index, old_value)


class ListField(base_field.BaseField):
    """__init__(*, sub_field, default=None, required=False)

    This field only allows a `list` type to be set as its value.

    If an entire list is set instead of singular values each entry in the new
    list has to match the subfield that was set when initialising the field.

    :param BaseField sub_field:
        Sets the field type that will be used for the entires of the list.
    """
    def __init__(self, sub_field, default=None, required=False):
        self.sub_field = sub_field
        super().__init__(default=default, required=required)
        self.value = ListWrapper(list_field=self)

    def update_by_index(self, index, value):
        self.document.update_sync('{}.{}'.format(self.name, index), value)

    def set_value(self, value):
        if not isinstance(value, list):
            raise errors.TypeMismatch(list, value)

        for item in value:
            self.validate(item)
        old_val = copy.deepcopy(self.value)
        sync_val = {}
        self.value.clear()
        self.value.extend(value)
        self.document.update_sync(name, old_val)

    def __getattr__(self, attr):
        path_split = attr.split('.')
        field_attr = path_split[0]

        if len(path_split) == 1:
            return super().__getattr__(attr)

        return self.value[int(path_split[1])]

    def validate_field(self, value):
        return self.sub_field.validate(value)
