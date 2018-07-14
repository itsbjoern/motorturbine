def deep_merge(original, update):
    for key, value in original.items():
        if key not in update:
            update[key] = value

        elif isinstance(value, dict):
            node = update.setdefault(key, {})
            deep_merge(value, node)

    return update


def item_by_path(container, path):
    split = path.split('.')
    index = split[0]

    if isinstance(container, list):
        if not index.isdigit():
            return None

        index = int(index)
        if len(container) < index:
            return None
        container = container[index]
    else:
        container = container.get(index, None)

    if container is None:
        return None

    if len(split) == 1:
        return container

    return item_by_path(container, '.'.join(split[1:]))


def get_sub_path(path, start, end=None, symbol='.'):
    """Returns a split subpath of a string by symbol.

    :param str path: The path to be split
    :param int start: The start index to be split off
    :param int end: Optional - The end index to be split off
    :param str symbol: Optional (*.*) - The symbol that will be used to cut the string
    :returns: The new subpatch as a string and a tuple with the start and end part that got cut off
    :rtype: :func:`tuple`
    """  # noqa
    split = path.split(symbol)
    result = split[start:]
    start_bit = split[:start]

    end_bit = []
    if end is not None:
        result = split[:(end - start)]
        end_bit = split[end:]

    cutoff = (symbol.join(start_bit), symbol.join(end_bit))
    return symbol.join(result), cutoff
