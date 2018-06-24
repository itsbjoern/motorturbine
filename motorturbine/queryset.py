class QueryBuilder(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        result = {}
        for name, op in self.items():
            if not isinstance(op, QueryOperator):
                op = Eq(op)

            result[name] = op()
        return result


class QueryOperator(object):
    """QueryOperators can be used to automatically generate
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


class Eq(QueryOperator):
    """Checks for any value that is equal to the given value.
     Not using it is the default case and functionally the same
    as just leaving out a QueryOperator completely.

    Example usage:

    >>> await Document.get_objects(num=5)
    >>> await Document.get_objects(num=Eq(5))

    Query:

    >>> Eq(5)()
    {'$eq': 5}
    """
    def __call__(self):
        return {'$eq': self.value}


class Ne(QueryOperator):
    """Checks for any value that is not equal to the given value.

    Example usage:

    >>> await Document.get_objects(num=Ne(5))

    Query:

    >>> Ne(5)()
    {'$ne': 5}
    """
    def __call__(self):
        return {'$ne': self.value}


class Lt(QueryOperator):
    """Checks for any value that is lesser than the given value.

    Example usage:

    >>> await Document.get_objects(num=Lt(5))

    Query:

    >>> Lt(5)()
    {'$lt': 5}
    """
    def __call__(self):
        return {'$lt': self.value}


class Lte(QueryOperator):
    """Checks for any value that is lesser than or equal to
    the given value.

    Example usage:

    >>> await Document.get_objects(num=Lte(5))

    Query:

    >>> Lte(5)()
    {'$lte': 5}
    """
    def __call__(self):
        return {'$lte': self.value}


class Gt(QueryOperator):
    """Checks for any value that is greater than the given value.

    Example usage:

    >>> await Document.get_objects(num=Gt(5))

    Query:

    >>> Gt(5)()
    {'$gt': 5}
    """
    def __call__(self):
        return {'$gt': self.value}


class Gte(QueryOperator):
    """Checks for any value that is greater than or equal to the given value.

    Example usage:

    >>> await Document.get_objects(num=Gte(5))

    Query:

    >>> Gte(5)()
    {'$gte': 5}
    """
    def __call__(self):
        return {'$gte': self.value}


class In(QueryOperator):
    """Checks for any value that is included in the given value.

    Example usage:

    >>> await Document.get_objects(num=In([1, 4, 5]))

    Query:

    >>> In([1, 4, 5])()
    {'$in': [1, 4, 5]}
    """
    def __call__(self):
        return {'$in': self.value}


class Nin(QueryOperator):
    """Checks for any value that is not included in the given value.

    Example usage:

    >>> await Document.get_objects(num=Nin([1, 4, 5]))

    Query:

    >>> Nin([1, 4, 5])()
    {'$nin': [1, 4, 5]}
    """
    def __call__(self):
        return {'$nin': self.value}
