class QueryBuilder(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        result = {}
        for name, op in self.items():
            if not isinstance(op, QueryOperator):
                op = eq(op)

            result[name] = op()
        return result


class QueryOperator(object):
    """QueryOperator can be used to automatically generate
    queries that are understood by mongo. Each of the operators
    can be used as defined in the mongo manual as they're just
    a direct mapping.
    See :class:`~motorturbine.document.BaseDocument` to use it with
    querying methods like
    :func:`~motorturbine.document.BaseDocument.get_objects`.
    """
    def __init__(self, value, requires_sync=True):
        super().__init__()
        self.value = value
        self.requires_sync = requires_sync


class eq(QueryOperator):
    """Checks for any value that is equal to the given value.
    Not using it is functionally the same as just leaving out
    a QueryOperator completely.

    Example usage:

    >>> await Document.get_objects(num=5)
    >>> await Document.get_objects(num=eq(5))

    Query:

    >>> eq(5)()
    {'$eq': 5}
    """
    def __call__(self):
        return {'$eq': self.value}


class ne(QueryOperator):
    """Checks for any value that is not equal to the given value.

    Example usage:

    >>> await Document.get_objects(num=neq(5))

    Query:

    >>> neq(5)()
    {'$neq': 5}
    """
    def __call__(self):
        return {'$ne': self.value}


class lt(QueryOperator):
    """Checks for any value that is lesser than the given value.

    Example usage:

    >>> await Document.get_objects(num=lt(5))

    Query:

    >>> lt(5)()
    {'$lt': 5}
    """
    def __call__(self):
        return {'$lt': self.value}


class lte(QueryOperator):
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


class gt(QueryOperator):
    """Checks for any value that is greater than the given value.

    Example usage:

    >>> await Document.get_objects(num=gt(5))

    Query:

    >>> gt(5)()
    {'$gt': 5}
    """
    def __call__(self):
        return {'$gt': self.value}


class gte(QueryOperator):
    """Checks for any value that is greater than or equal to the given value.

    Example usage:

    >>> await Document.get_objects(num=gte(5))

    Query:

    >>> gte(5)()
    {'$gte': 5}
    """
    def __call__(self):
        return {'$gte': self.value}


class isin(QueryOperator):
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


class nin(QueryOperator):
    """Checks for any value that is not included in the given value.

    Example usage:

    >>> await Document.get_objects(num=nin([1, 4, 5]))

    Query:

    >>> nin([1, 4, 5])()
    {'$nin': [1, 4, 5]}
    """
    def __call__(self):
        return {'$nin': self.value}
