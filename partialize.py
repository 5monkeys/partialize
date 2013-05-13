from inspect import getargspec
from itertools import imap, izip


class ArgumentMissing(KeyError, TypeError):
    pass


class ArgumentOverflow(IndexError, TypeError):
    pass


class InvalidKeyword(KeyError, TypeError):
    pass


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


def partialize(func):
    """
    Partial decorator/wrapper that returns a partial func.
    Arguments and keyword arguments can be modified and extended before the actual call through partial object.
    """
    _argspec = getargspec(func)
    _func_arg_names = _argspec.args[:-len(_argspec.defaults)]
    _func_kwarg_defaults = dict(izip(_argspec.args[-len(_argspec.defaults):], _argspec.defaults))

    class Partial(object):
        args = None
        kwargs = None

        def __init__(self, *args, **kwargs):
            try:
                arguments = NamedArguments(_func_arg_names, *args)
                keywords = KeywordArguments(_func_kwarg_defaults, **kwargs)
                super(Partial, self).__setattr__('args', arguments)
                super(Partial, self).__setattr__('kwargs', keywords)
            except IndexError:
                values = (func.__name__, len(_func_arg_names), len(args))
                raise ArgumentOverflow("Partial %s() got too many arguments, expected %i, got %i" % values)
            except KeyError:
                invalid_keys = list(set(kwargs) - set(_func_kwarg_defaults))
                raise InvalidKeyword("Partial %s() got unexpected keyword arguments %s" % (func.__name__, invalid_keys))

        def __call__(self, *args, **kwargs):
            new_kwargs = self.kwargs

            if kwargs:
                # Merge extra kwargs with existing
                try:
                    new_kwargs = new_kwargs.copy()
                    new_kwargs.update(**kwargs)
                except KeyError:
                    invalid_keys = list(set(kwargs) - set(_func_kwarg_defaults))
                    raise InvalidKeyword("Partial %s() got unexpected keyword arguments %s" % (func.__name__,
                                                                                               invalid_keys))
            # Get arguments as sorted args list and merge extra args
            try:
                new_args = self.args.as_tuple(*args)
            except KeyError:
                values = (func.__name__, len(_func_arg_names))
                raise ArgumentMissing('Partial %s() missing one or more arguments, expected % i' % values)
            except IndexError:
                values = (func.__name__, len(_func_arg_names))
                raise ArgumentOverflow("Partial %s() got too many arguments, expected %i" % values)

            return func(*new_args, **new_kwargs)

        def __setitem__(self, name, value):
            """
            Dispatch and set named argument to either args or kwargs
            """
            try:
                if name in self.args.names:
                    self.args[name] = value
                else:
                    self.kwargs[name] = value
            except KeyError:
                raise TypeError("Partial %s() got unexpected argument '%s'" % (func.__name__, name))

        __setattr__ = __setitem__

        def __getattr__(self, name):
            """
            Get named argument from either args or kwargs
            """
            if name in self.args.names:
                return self.args[name]
            elif name in self.kwargs:
                return self.kwargs[name]
            else:
                return super(Partial, self).__getattribute__(name)

        def update(self, E=None, **F):
            """
            Update args and/or kwargs
            """
            for name, value in (E or F).iteritems():
                self[name] = value

        def reset(self):
            """
            Reset partial args and kwargs to initial state
            """
            self.args.clear()
            self.kwargs.clear()

    func.partial = Partial
    return func
