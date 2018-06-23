from . import connection, queryset, errors


def Collection(cls):
    @classmethod
    def _get_collection(cls):
        c = connection.Connection()
        return c.database[cls.__name__]

    @classmethod
    async def get_objects(cls, **kwargs):
        """Queries the collection for multiple objects
        as defined by the supplied filters. For querying
        Motorturbine supplies its own functionality in form
        of :class:`QueryBlock`.
        """
        for name in kwargs:
            if not hasattr(cls, name):
                raise errors.FieldNotFound(name, cls.__name__)

        coll = cls._get_collection()
        builder = queryset.QueryBuilder(**kwargs)
        query = builder.construct()

        doc_data = coll.find(query)
        result = []
        async for data in doc_data:
            new_doc = cls(**data)
            result.append(new_doc)

        return result

    @classmethod
    async def get_object(cls, **kwargs):
        """Queries the collection for a single document
        Will return None if there is no or more than one document
        """

        objects = await cls.get_objects(**kwargs)

        if len(objects) == 1:
            return objects[0]

        return None

    setattr(cls, '_get_collection', _get_collection)
    setattr(cls, 'get_objects', get_objects)
    setattr(cls, 'get_object', get_object)
    return cls
