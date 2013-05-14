class ArgumentMissing(KeyError, TypeError):
    pass


class ArgumentOverflow(IndexError, TypeError):
    pass


class InvalidKeyword(KeyError, TypeError):
    pass
