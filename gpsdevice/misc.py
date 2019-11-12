
class Struct:
    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__dict__)


def int32(x):
    if x > 0xFFFFFFFF:
        raise OverflowError()
    if x > 0x7FFFFFFF:
        x = int(0x100000000 - x)
        if x < 2147483648:
            return -x
        else:
            return -2147483648
    return x


def int16(x):
    if x > 0xFFFF:
        raise OverflowError()
    if x > 0x7FFF:
        x = int(0x10000 - x)
        if x < 32768:
            return -x
        else:
            return -32768
    return x


def int8(x):
    if x > 0xFF:
        raise OverflowError()
    if x > 0x7F:
        x = int(0x100 - x)
        if x < 128:
            return -x
        else:
            return -128
    return x
