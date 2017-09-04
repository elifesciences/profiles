def remove_none_values(items):
    return dict(filter(lambda item: item[1] is not None, items.items()))
