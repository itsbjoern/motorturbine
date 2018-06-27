from .. import errors, updateset, utils
from . import base_field
import copy


class ListWrapper(list):
    def __init__(self, *args, list_field=None, **kwargs):
        self.list_field = list_field
        super().__init__(*args, **kwargs)

    def __contains__(self, value):
        for field in self:
            if field.value == value:
                return True
        return False

    def __delitem__(self, index):
        self.list_field.pull(index)
        super().__delitem__(index)

    def __setitem__(self, index, value):
        field = self.to_field(index, value)
        old_value = super().__getitem__(index).value
        self.list_field.set_index(index, old_value)
        list.__setitem__(self, index, field)

    def to_field(self, index, value):
        name = '{}.{}'.format(self.list_field.name, str(index))
        new_field = self.list_field.sub_field.clone(
            document=self.list_field.document, name=name)

        if index < len(self):
            field = list.__getitem__(self, index)
            new_field.set_value(field.value)
            new_field.synced()

            new_field.operator = field.operator
        new_field.set_value(value)
        return new_field

    def copy(self):
        return [item.value for item in self]

    def append(self, value):
        field = self.to_field(len(self), value)
        self.list_field.push(value)
        list.append(self, field)

    def __getitem__(self, index):
        item = super().__getitem__(index)
        if hasattr(item, 'value'):
            item = item.value
        return item


class ListField(base_field.BaseField):
    """__init__(sub_field, *, default=None, required=False, unique=False)

    This field only allows a `list` type to be set as its value.

    If an entire list is set instead of singular values each entry in the new
    list has to match the subfield that was set when initialising the field.

    :param BaseField sub_field:
        Sets the field type that will be used for the entires of the list.
    """
    def __init__(
            self,
            sub_field, *,
            default=None,
            required=False,
            unique=False,
            sync_enabled=True,
            document=None,
            name=None):
        super().__init__(
            default=default,
            required=required,
            unique=unique,
            sync_enabled=sync_enabled,
            document=document,
            name=name)
        self.sub_field = sub_field
        self.value = ListWrapper(list_field=self)

    def clone(self, *args, **kwargs):
        return super().clone(self.sub_field, **kwargs)

    def push(self, value):
        pass

    def pull(self, index):
        pass

    def set_index(self, index, value):
        pass

    def synced(self):
        super().synced()

        for index in range(len(self.value)):
            field = list.__getitem__(self.value, index)
            if hasattr(field, 'synced'):
                field.synced()

    def set_value(self, new_value):
        old_val = self.value.copy()
        new_operator = updateset.to_operator(self.value, new_value)
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
        self.value.extend(new_value)

    def get_operator(self, path):
        split = path.split('.')
        field = list.__getitem__(self.value, int(split[0]))
        return field.get_operator('.'.join(split[1:]))

    def __getattr__(self, attr):
        path_split = attr.split('.')
        field_attr = path_split[0]

        if len(path_split) == 1:
            return self.__getattribute__(attr)

        return self.value[int(path_split[1])]

    def validate_field(self, value):
        if not isinstance(value, list):
            raise errors.TypeMismatch(list, value)

        for item in value:
            self.sub_field.validate(item)
