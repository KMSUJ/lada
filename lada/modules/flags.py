def f(i):
    return 1 << (i - 1)


def assign(flagset, flag, value):
    if value:
        return hang(flagset, flag)
    else:
        return drop(flagset, flag)


def hang(flagset, flag):
    try:
        return flagset | flag
    except TypeError:
        return flag


def drop(flagset, flag):
    try:
        return flagset & ~flag
    except TypeError:
        return 0


def check(flagset, flag):
    try:
        return flagset & flag == flag
    except TypeError:
        return False
