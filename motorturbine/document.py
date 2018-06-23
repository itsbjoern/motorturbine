from . import errors, connection, fields
import types

special_attributes = ['fields']


class BaseDocument(object):
    """The BaseDocument is used to create new Documents
    which can be used to model your data structures.

    Simple example using a :class:`~motorturbine.fields.StringField`
    and an :class:`~motorturbine.fields.IntField`::

        class ExampleDocument(BaseDocument):
            name = StringField(default='myname')
            number = IntField(default=0)

    When instantiating a Document object it is possible to use keyword
    arguments to initialise its fields to the given values.

    >>> doc = ExampleDocument(name='Changed My Name', number=15)
    >>> print(doc)
    <ExampleDocument name='Changed My Name' number=15>
    >>> await doc.save()
    >>> print(doc)
    <ExampleDocument _id=ObjectId('$oid') name='Changed My Name' number=15>
    """
    fields = {}

    def __new__(cls, **kwargs):
        custom_fields = {}
        normals = dir(BaseDocument)
        doc = super(BaseDocument, cls).__new__(cls)

        # create general _id field
        id_field = fields.ObjectIdField(sync_enabled=False)
        id_field._connect_document(doc, '_id')
        object.__setattr__(doc, '_id', id_field)
        doc.fields = {'_id': id_field}

        for name, field in cls.__dict__.items():
            if name not in normals and not isinstance(field, types.MethodType):
                if not isinstance(field, fields.BaseField):
                    raise errors.FieldExpected(field)

                field._connect_document(doc, name)
                object.__setattr__(doc, name, field)
                doc.fields[name] = field

        # add attribute for syncs
        object.__setattr__(doc, '_sync_fields', {})

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

    def update_sync(self, name, value):
        self._sync_fields[name] = value

    def __getattribute__(self, attr):
        fields = super().__getattribute__('fields')

        path_split = attr.split('.')
        field_attr = path_split[0]
        field = fields.get(field_attr, None)

        if field is None:
            return super().__getattribute__(attr)

        if len(path_split) == 1:
            return field.value

        return getattr(field, '.'.join(path_split))

    async def save(self):
        """Calling the save method will start a synchronisation process with
        the database. Every change that was made since the last
        synchronisation is considered specifically to only update based on the
        condition that no fields that changed were updated in the meantime.
        In case that any conflicting fields did update we make sure to pull
        these changes first and only then update them to avoid critical write
        errors.
        """
        c = connection.Connection()
        coll = c.database[self.__class__.__name__]

        if self._id is None:
            insert_fields = {
                name: getattr(self, name)
                for name in self.fields if name != '_id'
            }
            doc = await coll.insert_one({**insert_fields})
            self._id = doc.inserted_id
        else:
            if len(self._sync_fields) == 0:
                return

            while True:
                updates = {
                    name: getattr(self, name) for name in self._sync_fields
                }
                projection = {'_id': 0}

                result = await coll.update_one(
                    {'_id': self._id, **self._sync_fields},
                    {'$set': updates})

                if result.matched_count == 1:
                    break

                changed_doc = await coll.find_one(
                    {'_id': self._id}, projection=projection)

                for name, val in changed_doc.items():
                    self.fields[name].set_value(val)

    def __repr__(self):
        field_rep = ''
        for name, field in self.fields.items():
            if name == '_id' and self._id is None:
                continue
            field_rep = field_rep + ' {}={}'.format(name, repr(field))

        return '<{}{}>'.format(self.__class__.__name__, field_rep)
