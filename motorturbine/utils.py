def deep_merge(original, update):
    for key, value in original.items():
        if key in update and isinstance(value, dict):
            node = update.setdefault(key, {})
            deep_merge(value, node)
        else:
            update[key] = value
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
