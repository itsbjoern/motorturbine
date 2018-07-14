from .. import errors, updateset, utils
from . import base_field
import uuid


class ListWrapper(list):
    def __init__(self, *args, list_field=None, **kwargs):
        self.list_field = list_field
        super().__init__(*args, **kwargs)

    def __eq__(self, other):
        return self.as_value() == other

    def __contains__(self, value):
        for field in self:
            if field.value == value:
                return True
        return False

    def __delitem__(self, index):
        item = super().__getitem__(index)
        del_str = '$$__mturbine_deleted'

        update = {
            'op': updateset.Set(del_str),
            'old_value': item.value
        }
        deletion = {
            'force_name': self.list_field.name,
            'op': updateset.Pull(del_str),
            'old_value': del_str
        }
        self.list_field.pseudo_operators[str(index)] = [update, deletion]

        field_name = self.list_field.name + '.' + str(index)
        self.list_field.document.update_sync(field_name)
        super().__delitem__(index)

    def __setitem__(self, index, value):
        field = self.to_field(index, value)
        old_value = super().__getitem__(index).value

        self.list_field.pseudo_operators.pop(str(index), None)
        list.__setitem__(self, index, field)

    def to_field(self, index, value, sync_field=True):
        name = '{}.{}'.format(self.list_field.name, str(index))
        new_field = self.list_field.sub_field.clone(
            document=self.list_field.document,
            name=name,
            sync_enabled=sync_field)

        if index < len(self):
            field = list.__getitem__(self, index)
            new_field.set_value(field.value)
            new_field.synced()

            new_field.updates = field.updates

        new_field.set_value(value)
        new_field.sync_enabled = True

        return new_field

    def append(self, value):
        field = self.to_field(len(self), value, sync_field=False)

        tmp_id = str(uuid.uuid4())
        update = {
            'force_name': self.list_field.name,
            'op': updateset.Push(value)
        }
        self.list_field.pseudo_operators[tmp_id] = [update]

        field_name = self.list_field.name + '.' + tmp_id
        self.list_field.document.update_sync(field_name)
        list.append(self, field)

    def extend(self, values):
        for value in values:
            self.append(value)

    def _extend(self, values):
        for value in values:
            field = self.to_field(len(self), value, sync_field=False)
            list.append(self, field)

    def __getitem__(self, index):
        item = super().__getitem__(index)
        return item.value

    def as_value(self):
        return [x.get_value() for x in self]


class ListField(base_field.BaseField):
    """__init__(sub_field, *, default=[], required=False, unique=False)

    This field only allows a `list` type to be set as its value.

    If an entire list is set instead of singular values each entry in the new
    list has to match the subfield that was set when initialising the field.

    :param BaseField sub_field:
        Sets the field type that will be used for the entires of the list.
    """
    def __init__(self, sub_field, **kwargs):
        kwargs['default'] = kwargs.pop('default', [])
        super().__init__(**kwargs)
        self.pseudo_operators = {}
        self.sub_field = sub_field
        self.value = ListWrapper(list_field=self)

    def clone(self, *args, **kwargs):
        return super().clone(self.sub_field, **kwargs)

    def synced(self):
        super().synced()
        self.pseudo_operators = {}

        if self.value is None:
            return

        for index in range(len(self.value)):
            field = list.__getitem__(self.value, index)
            if hasattr(field, 'synced'):
                field.synced()

    def set_value(self, new_value):
        old_val = None
        if self.value is not None:
            old_val = self.value.as_value()

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
            self.pseudo_operators = {}
        else:
            self.updates.append(update)

        if new_value is None:
            self.value = new_value
        else:
            self.value.clear()
            self.value._extend(new_value)

        if self.sync_enabled:
            self.document.update_sync(self.name)

    def get_updates(self, path):
        if path == '':
            # we need to make sure that if there is a set update on the map
            # each update is actually a value representation of its field
            # instead of the field itself (or document)
            for update in self.updates:
                op = update['op']
                for index, field in enumerate(op.update):
                    as_field = self.sub_field.clone(sync_enabled=False)
                    as_field.set_value(field)
                    op.update[index] = as_field.get_value()

                old = update['old_value']
                for index, field in enumerate(old):
                    if isinstance(field, base_field.BaseField):
                        old[index] = field.get_value()

            return self.updates

        sub_path, cutoff = utils.get_sub_path(path, 1)
        index = cutoff[0]

        val = self.pseudo_operators.get(index, None)
        if val is not None:
            return val

        field = list.__getitem__(self.value, int(index))

        return field.get_updates(sub_path)

    def __getattr__(self, attr):
        path_split = attr.split('.')
        field_attr = path_split[0]
        if len(path_split) == 1:
            return self.__getattribute__(attr)

        return self.value[int(path_split[1])]

    def validate_field(self, value):
        if not isinstance(value, list):
            raise errors.TypeMismatch(list, type(value))

    def get_value(self):
        if self.value is None:
            return None
        return self.value.as_value()
