def to_operator(current, new_value):
    is_operator = isinstance(new_value, UpdateOperator)
    is_set = isinstance(new_value, Set)

    if is_operator:
        if not is_set and current is None:
            raise Exception('Cant use operator on None')
    else:
        new_value = Set(new_value)

    return new_value


class UpdateOperator(object):
    """UpdateOperators can be used to automatically generate
    update queries that are understood by mongo. Each of the operators
    can be used as defined in the mongo manual as they're just
    a direct mapping.
    """
    def __init__(self, update):
        super().__init__()
        self.update = update

    def set_original_value(self, value):
        self.original_value = value


class Set(UpdateOperator):
    """Is used to set the specified field to any given value.
    Not using it is the default case and
    functionally the same as just leaving out an UpdateOperator completely.

    Example usage:

    >>> doc.num = 5
    >>> doc.num = Set(5)

    Query:

    >>> Set(5)()
    {'$set': 5}
    """
    def __call__(self):
        return '$set', self.update

    def apply(self):
        return self.update


class Unset(UpdateOperator):
    """Is used to remove an entry from a list or dict.

    Example usage:

    >>> del doc.map['test']
    >>> doc.map = Unset('test')

    Query:

    >>> Unset('test')()
    {'$unset': 'test'}
    """
    def __call__(self):
        return '$unset', self.update

    def apply(self):
        return self.update


class Inc(UpdateOperator):
    """Is used to modify a numeric value by a given amount.

    Example usage:

    >>> doc.num = Inc(5)
    >>> doc.num = Inc(-5)

    Query:

    >>> Inc(5)()
    {'$inc': 5}
    """
    def __call__(self):
        return '$inc', self.update

    def apply(self):
        return self.original_value + self.update


class Dec(UpdateOperator):
    """Is used to decrease a numeric value.

    Example usage:

    >>> doc.num = Dec(5)

    Query:

    >>> Dec(5)()
    {'$inc': -5}
    """
    def __call__(self):
        return '$inc', -self.update

    def apply(self):
        return self.original_value - self.update


class Max(UpdateOperator):
    """Update the field to the maximum of database and current value.

    Example usage:

    >>> doc.num = Max(5)

    Query:

    >>> Max(5)()
    {'$max': 5}
    """
    def __call__(self):
        return '$max', self.update

    def apply(self):
        return max(self.original_value, self.update)


class Min(UpdateOperator):
    """Update the field to the minimum of database and current value.

    Example usage:

    >>> doc.num = Min(5)

    Query:

    >>> Min(5)()
    {'$min': 5}
    """
    def __call__(self):
        return '$min', self.update

    def apply(self):
        return min(self.original_value, self.update)


class Mul(UpdateOperator):
    """Is used to multipy a numeric value by a given amount.

    Example usage:

    >>> doc.num = Mul(5)

    Query:

    >>> Mul(5)()
    {'$mul': 5}
    """
    def __call__(self):
        return '$mul', self.update

    def apply(self):
        return self.original_value * self.update


class Push(UpdateOperator):
    """Is used to append a value to a list.

    Example usage:

    >>> doc.num_list = Push(5)

    Query:

    >>> Push(5)()
    {'$push': 5}
    """
    def __call__(self):
        return '$push', self.update

    def apply(self):
        return self.original_value.append(self.update)


class Pull(UpdateOperator):
    """Is used to pull all entries that match the given value.

    Example usage:

    >>> doc.num_list = Pull(5)

    Query:

    >>> Pull(5)()
    {'$pull': 5}
    """
    def __call__(self):
        return '$pull', self.update

    def apply(self):
        return [
            val for val in self.original_value
            if val != self.update
        ]


class PullAll(UpdateOperator):
    """Is used to pull all entries that match a value from a list.

    Example usage:

    >>> doc.num_list = PullAll([5, 6, 7])

    Query:

    >>> PullAll([5, 6, 7])()
    {'$pullAll': [5, 6, 7]}
    """
    def __call__(self):
        return '$pullAll', self.update

    def apply(self):
        return [
            val for val in self.original_value
            if val not in self.update
        ]
