def to_operator(current, new_value):
    is_operator = isinstance(new_value, UpdateOperator)
    is_set = isinstance(new_value, setval)

    if is_operator:
        if not is_set and current is None:
            raise Exception('Cant use operator on None')
    else:
        new_value = setval(new_value)

    return new_value


class UpdateOperator(object):
    """UpdateOperator can be used to automatically generate
    update queries that are understood by mongo. Each of the operators
    can be used as defined in the mongo manual as they're just
    a direct mapping.
    """
    def __init__(self, update):
        super().__init__()
        self.update = update

    def set_original_value(self, value):
        self.original_value = value


class setval(UpdateOperator):
    """
    Example usage:

    >>> doc.num = inc(5)

    Query:

    >>> inc(5)()
    {'$inc': 5}
    """
    def __call__(self):
        return '$set', self.update

    def apply(self):
        return self.update


class inc(UpdateOperator):
    """
    Example usage:

    >>> doc.num = inc(5)

    Query:

    >>> inc(5)()
    {'$inc': 5}
    """
    def __call__(self):
        return '$inc', self.update

    def apply(self):
        return self.original_value + self.update
