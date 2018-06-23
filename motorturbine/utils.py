def deep_merge(original, update):
    for key, value in original.items():
        if key in update and isinstance(value, dict):
            node = update.setdefault(key, {})
            deep_merge(value, node)
        else:
            update[key] = value
    return update
