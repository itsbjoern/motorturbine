from . import errors, connection, fields
import types
import copy

protected_fields = ['_id']
special_attributes = ['fields', '_BaseDocument__sync_fields']


class BaseDocument(object):
    _id = None
    fields = {}

    def __new__(cls, **kwargs):
        custom_fields = {}
        normals = dir(BaseDocument)
        doc = super(BaseDocument, cls).__new__(cls)

        id_field = fields.ObjectIdField()

        object.__setattr__(doc, '_id', id_field)
        doc.fields = {'_id': id_field}

        for name, field in cls.__dict__.items():
            if name not in normals and not isinstance(field, types.MethodType):
                if not isinstance(field, fields.BaseField):
                    raise errors.FieldExpected(field)

                object.__setattr__(doc, name, field)
                doc.fields[name] = field

        return doc

    def __init__(self, **kwargs):
        for name, field in self.fields.items():
            if name in kwargs:
                field.set_value(kwargs.get(name))

    def __setattr__(self, attr, value):
        if attr in special_attributes:
            return super().__setattr__(attr, value)
        field = self.fields.get(attr, None)

        if field is None:
            raise Exception('field not set')

        field.set_value(value)

    def __getattribute__(self, attr):
        val = super().__getattribute__(attr)
        if attr in special_attributes:
            return val

        fields = super().__getattribute__('fields')
        field = fields.get(attr, None)
        if field is None:
            return val
        return field.value

    async def save(self):
        c = connection.Connection()
        coll = c.database[self.__class__.__name__]

        if self._id is None:
            insert_fields = {
                name: getattr(self, name)
                for name in self.fields if name not in protected_fields
            }
            doc = await coll.insert_one({**insert_fields})
            self._id = doc.inserted_id
        else:
            old_fields = {}
            update_operations = {}

            for name in self.fields:
                field = self.fields[name]
                if not field.did_change():
                    continue

                old, update = field.get_query_value(name)
                old_fields.update(old)

                update_operations = {
                    key: {
                        **update_operations.get(key, {}),
                        **update.get(key, {})
                    }
                    for key in set([*update.keys(), *update_operations.keys()])
                }

            while True:
                result = await coll.update_one({
                    '_id': self._id,
                    **old_fields
                }, update_operations)

                if result.modified_count == 1:
                    for field in self.fields.values():
                        field.synced()
                    break

                needed = {name: 1 for name in old_fields}
                needed['_id'] = 0
                doc = await coll.find_one({'_id': self._id}, needed)
                old_fields = {}
                for name in doc:
                    partial = name.split('.')[0]
                    old_fields[name] = doc[partial]
