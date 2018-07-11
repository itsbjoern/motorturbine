from . import errors, collection, fields, updateset, utils
import types
import copy
from pymongo import errors as pymongo_errors, UpdateOne


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
    <ExampleDocument id=ObjectId('$oid') name='Changed My Name' number=15>

    :raises FieldNotFound: On access of a non-existent field
    """

    def __new__(cls, **kwargs):
        normals = dir(BaseDocument)
        doc = super(BaseDocument, cls).__new__(cls)
        object.__setattr__(doc, '_fields', {})
        doc_fields = object.__getattribute__(doc, '_fields')

        # add attribute for syncs
        object.__setattr__(doc, '_sync_fields', [])

        # create general id field
        id_field = fields.ObjectIdField(
            sync_enabled=False, document=doc, name='id')

        doc_fields['id'] = id_field
        coll = cls._get_collection()

        for name, field in cls.__dict__.items():
            if name not in normals and not isinstance(field, types.MethodType):
                if not isinstance(field, fields.BaseField):
                    raise errors.FieldExpected(field)

                field = copy.deepcopy(field)
                field.document = doc
                field.name = name

                doc_fields[name] = field

                if field.unique:
                    coll.create_index(field.name, unique=True)
        return doc

    def __init__(self, **kwargs):
        super().__init__()

        kwargs['id'] = kwargs.pop('_id', None)
        for name, field in self._get_fields().items():
            field.set_value(kwargs.pop(name, field.default))
            field.synced()
        if len(kwargs) != 0:
            key = next(iter(kwargs))
            raise errors.FieldNotFound(key, self)

    def _get_fields(self):
        return object.__getattribute__(self, '_fields')

    def _get_sync_fields(self):
        return object.__getattribute__(self, '_sync_fields')

    def __setattr__(self, attr, value):
        field = self._get_fields().get(attr, None)

        if field is None:
            raise errors.FieldNotFound(attr, self)

        field.set_value(value)

    def update_sync(self, name):
        sync_fields = self._get_sync_fields()
        if name not in sync_fields:
            sync_fields.append(name)

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
        field_attr = utils.get_sub_path(attr, 0, 1)
        field = fields.get(field_attr, None)

        if field is None:
            raise errors.FieldNotFound(attr, self)

        if len(path_split) == 1:
            return field.value

        sub_path = utils.get_sub_path(attr, 1)
        return getattr(field, sub_path)

    async def get_reference(self, field_name, collections=None):
        """When using :class:`~motorturbine.fields.ReferenceField` this method allows
        loading the reference by the fields name.
        Returns `None` if the given field exists but is not a :class:`~motorturbine.fields.ReferenceField` type.

        :param str field_name: The name of the ReferenceField
        :param list collections: optional (*None*) –
            A list of :class:`~motorturbine.document.BaseDocument` classes.
            In case you allowed subclassing in a
            :class:`~motorturbine.fields.ReferenceField` you can specify
            the additional document collections that will be searched if they are
            not the same as the specified documents type.

        :raises FieldNotFound: On access of a non-existent field
        """  # noqa
        doc_fields = self._get_fields()
        field = doc_fields.get(field_name, None)

        if field is None:
            raise errors.FieldNotFound(field_name, self)

        if not isinstance(field, fields.ReferenceField):
            return None

        oid = getattr(self, field_name)

        reference_doc = field.reference_doc
        ref = await reference_doc.get_object(id=oid)

        if ref is None and collections is not None:
            if not isinstance(collections, list):
                raise errors.TypeMismatch(list, collections.__class__)
            for coll in collections:
                ref = await coll.get_object(id=oid)
                if ref is not None:
                    break

        return ref

    async def save(self, limit=0):
        """Calling the save method will start a synchronisation process with
        the database. Every change that was made since the last
        synchronisation is considered specifically to only update based on the
        condition that no fields that changed were updated in the meantime.
        In case that any conflicting fields did update we make sure to pull
        these changes first and only then update them to avoid critical write
        errors.

        If a document has not been saved before the 'id' field will be set
        automatically after the update is done.

        :param int limit: optional *(0)* –
            The maximum amount of tries before a save operation fails.
            Can be used as a way to catch problematic state or to probe if the
            current document has changed yet if set to 1.

        :raises RetryLimitReached: Raised if limit is reached
        """
        coll = self.__class__._get_collection()
        doc_fields = self._get_fields()
        sync_fields = self._get_sync_fields()
        if self.id is None:
            insert_fields = {
                name: getattr(self, name)
                for name in doc_fields if name != 'id'
            }

            doc = await coll.insert_one({**insert_fields})
            self.id = doc.inserted_id
            for field in doc_fields.values():
                sync_fields.clear()
                field.synced()
        else:
            if len(sync_fields) == 0:
                return

            tries = 0
            while True:
                bulk_updates = []
                for path in sync_fields:
                    split = path.split('.')
                    name = split[0]

                    sub_path = utils.get_sub_path(path, 1)

                    ops = doc_fields[name].get_updates(sub_path)

                    assert isinstance(ops, list)
                    if len(ops) == 0:
                        continue

                    zippable = True
                    updates = []
                    for val in ops:
                        op, new_value = val['op']()

                        update_name = val.get('force_name', path)
                        if update_name != path:
                            zippable = False
                        update = {
                            'filter': {},
                            'update': {op: {update_name: new_value}}
                        }
                        if 'old_value' in val:
                            update['filter'] = {path: val['old_value']}

                        updates.append(update)
                    if zippable:
                        bulk_updates = list(zip(*bulk_updates, updates))
                    else:
                        bulk_updates.extend([[up] for up in updates])

                update_queries = []
                for bulk in bulk_updates:
                    bulk_filter = {'_id': self.id}
                    bulk_update = {}
                    for item in bulk:
                        bulk_filter = {**bulk_filter, **item['filter']}
                        bulk_update = utils.deep_merge(
                            bulk_update, item['update'])

                        single_update = UpdateOne(bulk_filter, bulk_update)
                        update_queries.append(single_update)
                try:
                    result = await coll.bulk_write(update_queries)
                    mongo_result = result.bulk_api_result
                except pymongo_errors.BulkWriteError as e:
                    print(e.details)
                    raise e

                if result.matched_count == len(update_queries):
                    sync_fields.clear()

                    for field in doc_fields.values():
                        field.synced()
                    break

                tries += 1
                if limit != 0 and tries >= limit:
                    raise errors.RetryLimitReached(limit, self)

                projection = {'_id': 0}
                changed_doc = await coll.find_one(
                    {'_id': self.id}, projection=projection)

                for name, val in changed_doc.items():
                    for path in sync_fields:
                        item = utils.item_by_path(changed_doc, path)
                        if item is not None:
                            sub_path = utils.get_sub_path(path, 1)
                            for x in doc_fields[name].get_updates(sub_path):
                                x['old_value'] = item

    def __repr__(self):
        field_rep = ''
        doc_fields = self._get_fields()
        for name, field in doc_fields.items():
            if name == 'id' and self.id is None:
                continue
            field_rep = field_rep + ' {}={}'.format(name, repr(field))

        return '<{}{}>'.format(self.__class__.__name__, field_rep)
