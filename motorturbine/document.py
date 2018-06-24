from . import errors, collection, fields, updateset, utils
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

        # add attribute for syncs
        object.__setattr__(doc, '_sync_fields', {})

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
            else:
                field.validate(field.default)

    def __setattr__(self, attr, value):
        field = self._get_fields().get(attr, None)

        if field is None:
            raise errors.FieldNotFound(attr, self)

        field.set_value(value)

    def update_sync(self, name, value):
        sync_fields = self._get_sync_fields()
        sync_fields.setdefault(name, value)

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

        return getattr(field, '.'.join(path_split[1:]))

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
        fields = self._get_fields()
        sync_fields = self._get_sync_fields()
        if self._id is None:
            insert_fields = {
                name: getattr(self, name)
                for name in fields if name != '_id'
            }

            doc = await coll.insert_one({**insert_fields})
            self._id = doc.inserted_id
            for field in fields.values():
                sync_fields.clear()
                field.synced()
        else:
            if len(sync_fields) == 0:
                return

            tries = 0
            while True:
                updates = {}
                for path in sync_fields:
                    split = path.split('.')
                    name = split[0]
                    val = fields[name].get_operator('.'.join(split[1:]))
                    assert isinstance(val, updateset.UpdateOperator)

                    op, value = val()
                    update = {op: {path: value}}
                    updates = utils.deep_merge(updates, update)
                projection = {'_id': 0}

                result = await coll.update_one(
                    {'_id': self._id, **sync_fields},
                    updates)

                if result.matched_count == 1:
                    sync_fields.clear()

                    for field in fields.values():
                        field.synced()
                    break

                tries += 1
                if limit != 0 and tries >= limit:
                    raise errors.RetryLimitReached(limit, self)

                changed_doc = await coll.find_one(
                    {'_id': self._id}, projection=projection)

                for name, val in changed_doc.items():
                    for path in sync_fields:
                        item = utils.item_by_path(changed_doc, path)
                        if item is not None:
                            sync_fields[path] = item
                    # if needs_update:
                    #     fields[name] = val

    def __repr__(self):
        field_rep = ''
        fields = self._get_fields()
        for name, field in fields.items():
            if name == '_id' and self._id is None:
                continue
            field_rep = field_rep + ' {}={}'.format(name, repr(field))

        return '<{}{}>'.format(self.__class__.__name__, field_rep)
