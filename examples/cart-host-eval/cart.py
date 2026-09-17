def add_item(items, name, quantity=1):
    result = dict(items)
    result[name] = quantity
    return result
