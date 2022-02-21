registry = {}
type_funcs = {type(list()): list, type(tuple()): tuple}


def type_register(input_type):
    def register(func):
        registry[input_type] = func
        return func

    return register


def lower_strings_dispatch(value):
    if func := registry.get(type(value), None):
        return func(value)
    return value


@type_register(type(None))
def lower_strings(value):
    return


@type_register(str)
def lower_strings(value):
    return value.lower()


@type_register(dict)
def lower_strings(user_dict):
    cleaned = {}
    for key, value in user_dict.items():
        lowered_key = lower_strings_dispatch(key)
        lowered_value = lower_strings_dispatch(value)

        cleaned[lowered_key] = lowered_value
    return cleaned


@type_register(tuple)
@type_register(list)
def lower_strings(iterable):
    type_func = type_funcs[type(iterable)]
    lowered = []
    for val in iterable:
        lowered_val = lower_strings_dispatch(val)
        lowered.append(lowered_val)
    return type_func(lowered)


test_dict = {'list': ['Hi', ('How', 'Are')]
    , 'dict': {'You': 1, 'Today': {'Doing': 'Lukas'}}
    , 'int': 1
    , 'none': None}
