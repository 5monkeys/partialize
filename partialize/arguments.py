from itertools import imap


class NamedArguments(dict):

    def __init__(self, names, *args):
        super(NamedArguments, self).__init__()
        self.initial = args
        self.names = set(names)
        self.max_args = len(names)
        self.extend(args)

    def __setitem__(self, name, value):
        if name in self.names:
            super(NamedArguments, self).__setitem__(name, value)
        else:
            raise KeyError("Invalid argument name '%s'" % name)

    def get_next_name(self):
        try:
            return tuple(self.names)[len(self)]
        except IndexError:
            raise IndexError('Too many arguments, expected %i' % self.max_args)

    def append(self, value):
        name = self.get_next_name()
        super(NamedArguments, self).__setitem__(name, value)

    def extend(self, iterable):
        map(self.append, iterable)

    def clear(self):
        super(NamedArguments, self).clear()
        self.extend(self.initial)

    def as_tuple(self, *more_args):
        """
        Returns sorted arguments. Raises KeyError if one is missing.
        """
        args = self

        if more_args:
            args = args.copy()
            remaining_names = tuple(self.names)[len(self):]
            for i, arg in enumerate(more_args):
                args[remaining_names[i]] = arg  # May raise IndexError if too many 'more_args'

        return tuple(args[name] for name in self.names)  # May raise KeyError if missing args

    def as_kwargs(self, *more_args):
        kwargs = self

        if more_args:
            kwargs = kwargs.copy()
            remaining_names = tuple(self.names)[len(self):]
            for i, arg in enumerate(more_args):
                kwargs[remaining_names[i]] = arg  # May raise IndexError if too many 'more_args'

        return kwargs


class KeywordArguments(dict):

    def __init__(self, defaults=None, **kwargs):
        super(KeywordArguments, self).__init__()
        self.defaults = defaults
        self.initial = kwargs
        self.clear()
        self.update(kwargs)

    def __setitem__(self, key, value):
        if self.is_valid_keyword(key):
            super(KeywordArguments, self).__setitem__(key, value)
        else:
            raise KeyError("'%s' is not a valid keyword argument" % key)

    def update(self, E=None, **F):
        keys = (E or F).keys()
        if not self.is_valid_keywords(*keys):
            raise KeyError('%s contains invalid keyword arguments' % keys)
        if E:
            super(KeywordArguments, self).update(E)
        else:
            super(KeywordArguments, self).update(**F)

    def clear(self):
        super(KeywordArguments, self).clear()
        if self.defaults:
            for key, value in self.defaults.iteritems():
                self.setdefault(key, value)
        self.update(self.initial)

    def copy(self):
        clone = KeywordArguments(self.defaults)
        super(KeywordArguments, clone).update(self)
        return clone

    def is_valid_keyword(self, name):
        return not self or name in self

    def is_valid_keywords(self, *names):
        return all(imap(self.is_valid_keyword, names))
