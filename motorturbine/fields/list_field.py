from .. import errors
from . import base_field


class ListWrapper(list):
    old_list = None

    def __getitem__(self, index):
        return super().__getitem__(index)

    def __delitem__(self, index):
        del self.query[index]
        super().__delitem__(index)

    def __len__(self):
        return super().__len__()

    def __setitem__(self, index, value):
        if self.old_list is None:
            self.old_list = {}
        self.old_list[index] = self.__getitem__(index)
        super().__setitem__(index, value)

    def insert(self, index, value):
        super().insert(index, value)


class ListField(base_field.BaseField):
    def __init__(self, sub_field, default=None):
        self.sub_field = sub_field
        super().__init__()
        self.value = ListWrapper()

    def validate_field(self, value):
        return self.sub_field.validate(value)

    def did_change(self):
        return len(self.value.old_list.keys()) > 0

    def synced(self):
        self.value.old_list = None

    def get_query(self, name):
        updates = {
            '{}.{}'.format(name, index): self.value[index]
            for index in self.value.old_list
        }
        old = {
            '{}.{}'.format(name, index): value
            for index, value in self.value.old_list.items()
        }
        return {name: old}, {'$set': updates}
