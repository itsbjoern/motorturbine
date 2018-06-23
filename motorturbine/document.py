from . import errors, collection, fields
import types
import copy


@collection.Collection
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

    :raises FieldNotFound: On access of a non-existent field
    """

    def __new__(cls, **kwargs):
        normals = dir(BaseDocument)
        doc = super(BaseDocument, cls).__new__(cls)
        object.__setattr__(doc, '_fields', {})
        doc_fields = object.__getattribute__(doc, '_fields')

        # create general _id field
        id_field = fields.ObjectIdField(sync_enabled=False)
        id_field._connect_document(doc, '_id')

        doc_fields['_id'] = id_field

        for name, field in cls.__dict__.items():
            if name not in normals and not isinstance(field, types.MethodType):
                if not isinstance(field, fields.BaseField):
                    raise errors.FieldExpected(field)

                field = copy.deepcopy(field)
                field._connect_document(doc, name)
                doc_fields[name] = field

        # add attribute for syncs
        object.__setattr__(doc, '_sync_fields', {})

        return doc

    def _get_fields(self):
        return object.__getattribute__(self, '_fields')

    def _get_sync_fields(self):
        return object.__getattribute__(self, '_sync_fields')

    def __init__(self, **kwargs):
        super().__init__()
        for name, field in self._get_fields().items():
            if name in kwargs:
                field.set_value(kwargs.get(name))

    def __setattr__(self, attr, value):
        field = self._get_fields().get(attr, None)

        if field is None:
            raise errors.FieldNotFound(attr, self)

        field.set_value(value)

    def update_sync(self, name, value):
        self._get_sync_fields()[name] = value

    def __getattribute__(self, attr):
        # mimic hasattr
        try:
            val = object.__getattribute__(self, attr)
            if attr in dir(object) or isinstance(val, types.MethodType):
                return val
        except AttributeError:
            pass

        fields = self._get_fields()
        path_split = attr.split('.')
        field_attr = path_split[0]
        field = fields.get(field_attr, None)

        if field is None:
            raise errors.FieldNotFound(attr, self)

        if len(path_split) == 1:
            return field.value

        return getattr(field, '.'.join(path_split))

    async def save(self, limit=0):
        """Calling the save method will start a synchronisation process with
        the database. Every change that was made since the last
        synchronisation is considered specifically to only update based on the
        condition that no fields that changed were updated in the meantime.
        In case that any conflicting fields did update we make sure to pull
        these changes first and only then update them to avoid critical write
        errors.

        If a document has not been saved before the '_id' field will be set
        automatically after the update is done.

        :param int limit: optional *(0)* –
            The maximum amount of tries before a save operation fails.
            Can be used as a way to catch problematic state or to probe if the
            current document has changed yet if set to 1.

        :raises RetryLimitReached: Raised if limit is reached
        """
        coll = self.__class__._get_collection()

        if self._id is None:
            insert_fields = {
                name: getattr(self, name)
                for name in self._get_fields() if name != '_id'
            }
            doc = await coll.insert_one({**insert_fields})
            self._id = doc.inserted_id
        else:
            sync_fields = self._get_sync_fields()
            if len(sync_fields) == 0:
                return

            tries = 0
            while True:
                updates = {
                    name: getattr(self, name) for name in sync_fields
                }
                projection = {'_id': 0}

                result = await coll.update_one(
                    {'_id': self._id, **sync_fields},
                    {'$set': updates})

                if result.matched_count == 1:
                    break

                tries += 1
                if limit != 0 and tries >= limit:
                    raise errors.RetryLimitReached(limit, self)

                changed_doc = await coll.find_one(
                    {'_id': self._id}, projection=projection)

                fields = self._get_fields()
                for name, val in changed_doc.items():
                    if name not in sync_fields:
                        fields[name].value = val
                    sync_fields[name] = val

    def __repr__(self):
        field_rep = ''
        fields = self._get_fields()
        for name, field in fields.items():
            if name == '_id' and self._id is None:
                continue
            field_rep = field_rep + ' {}={}'.format(name, repr(field))

        return '<{}{}>'.format(self.__class__.__name__, field_rep)
