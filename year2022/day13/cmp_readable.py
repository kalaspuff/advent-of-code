"""
def cmp_readable(*args):
    for pair in list(zip(*args)):
        if list in map(type, pair):
            retval = cmp(*map(lambda x: [x] if isinstance(x, int) else x, pair))
        else:
            retval = cmp(*map(lambda x: [[]] * x, pair))
        if retval != 0:
            return retval
    return max(min(1, operator.sub(*map(len, args))), -1)
"""
