from inspect import getargspec
from itertools import izip
from partialize.arguments import NamedArguments, KeywordArguments
from partialize.exceptions import ArgumentMissing, ArgumentOverflow, InvalidKeyword


__all__ = ['partialize']


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
