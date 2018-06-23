class QueryBuilder(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        result = {}
        for name, block in self.items():
            if not isinstance(block, QueryBlock):
                block = eq(block)

            result[name] = block()
        return result


class QueryBlock(object):
    """QueryBlocks can be used to automatically generate
    queries that are understood by mongo. Each of the blocks
    can be used as defined in the mongo manual as they're just
    a direct mapping.
    See :class:`~motorturbine.document.BaseDocument` to use it with
    querying methods like
    :func:`~motorturbine.document.BaseDocument.get_objects`.
    """
    def __init__(self, value):
        super().__init__()
        self.value = value


class eq(QueryBlock):
    """Checks for any value that is equal to the given value.
    Not using it is functionally the same as just leaving out
    a QueryBlock completely.

    Example usage:

    >>> await Document.get_objects(num=5)
    >>> await Document.get_objects(num=eq(5))

    Query:

    >>> eq(5)()
    {'$eq': 5}
    """
    def __call__(self):
        return {'$eq': self.value}


class ne(QueryBlock):
    """Checks for any value that is not equal to the given value.

    Example usage:

    >>> await Document.get_objects(num=neq(5))

    Query:

    >>> neq(5)()
    {'$neq': 5}
    """
    def __call__(self):
        return {'$ne': self.value}


class lt(QueryBlock):
    """Checks for any value that is lesser than the given value.

    Example usage:

    >>> await Document.get_objects(num=lt(5))

    Query:

    >>> lt(5)()
    {'$lt': 5}
    """
    def __call__(self):
        return {'$lt': self.value}


class lte(QueryBlock):
    """Checks for any value that is lesser than or equal to
    the given value.

    Example usage:

    >>> await Document.get_objects(num=lte(5))

    Query:

    >>> lte(5)()
    {'$lte': 5}
    """
    def __call__(self):
        return {'$lte': self.value}


class gt(QueryBlock):
    """Checks for any value that is greater than the given value.

    Example usage:

    >>> await Document.get_objects(num=gt(5))

    Query:

    >>> gt(5)()
    {'$gt': 5}
    """
    def __call__(self):
        return {'$gt': self.value}


class gte(QueryBlock):
    """Checks for any value that is greater than or equal to the given value.

    Example usage:

    >>> await Document.get_objects(num=gte(5))

    Query:

    >>> gte(5)()
    {'$gte': 5}
    """
    def __call__(self):
        return {'$gte': self.value}


class isin(QueryBlock):
    """Checks for any value that is included in the given value.
    To enable usage as a direct import the mongo operator 'in'
    was renamed to 'isin'.

    Example usage:

    >>> await Document.get_objects(num=isin([1, 4, 5]))

    Query:

    >>> isin([1, 4, 5])()
    {'$in': [1, 4, 5]}
    """
    def __call__(self):
        return {'$in': self.value}


class nin(QueryBlock):
    """Checks for any value that is not included in the given value.

    Example usage:

    >>> await Document.get_objects(num=nin([1, 4, 5]))

    Query:

    >>> nin([1, 4, 5])()
    {'$nin': [1, 4, 5]}
    """
    def __call__(self):
        return {'$nin': self.value}
