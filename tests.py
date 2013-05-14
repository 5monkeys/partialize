import unittest
from partialize import partialize, get_version
from partialize.arguments import NamedArguments, KeywordArguments
from partialize.exceptions import ArgumentMissing, ArgumentOverflow, InvalidKeyword


@partialize
def single_arg_func(a, kw_a=None, kw_b=False):
    return a, kw_a, kw_b


@partialize
def multi_arg_func(a, b, kw_a=None, kw_b=True):
    return a, b, kw_a, kw_b


class NamedArgumentsTest(unittest.TestCase):

    names = ('na', 'nb', 'nc')

    def test_initial_args(self):
        args = NamedArguments(self.names, 'a')
        self.assertEqual(args['na'], 'a')
        self.assertRaises(KeyError, args.as_tuple)

    def test_extend_args(self):
        args = NamedArguments(self.names, 'a')
        args.extend(['b', 'c'])
        arg_list = args.as_tuple()
        self.assertTupleEqual(arg_list, ('a', 'b', 'c'))

    def test_append_arg(self):
        args = NamedArguments(self.names, 'a', 'b')
        args.append('c')
        arg_list = args.as_tuple()
        self.assertTupleEqual(arg_list, ('a', 'b', 'c'))

    def test_set_arg(self):
        args = NamedArguments(self.names, 'a')
        args['nb'] = 'b'
        self.assertRaises(KeyError, args.as_tuple)
        args['nc'] = 'c'
        arg_list = args.as_tuple()
        self.assertTupleEqual(arg_list, ('a', 'b', 'c'))
        self.assertRaises(KeyError, args.__setitem__, 'd', 'd')

    def test_more_args(self):
        args = NamedArguments(self.names, 'a', 'b')
        arg_list = args.as_tuple('c')
        self.assertTupleEqual(arg_list, ('a', 'b', 'c'))
        self.assertRaises(IndexError, args.as_tuple, 'c', 'd')

    def test_clear(self):
        args = NamedArguments(self.names, 'a', 'b')
        args['nc'] = 'c'
        arg_list = args.as_tuple()
        self.assertTupleEqual(arg_list, ('a', 'b', 'c'))
        args.clear()
        self.assertRaises(KeyError, args.as_tuple)
        args['nc'] = 'c2'
        arg_list = args.as_tuple()
        self.assertTupleEqual(arg_list, ('a', 'b', 'c2'))

    def test_as_kwargs(self):
        args = NamedArguments(self.names, 'a', 'b')
        self.assertDictEqual(args.as_kwargs(), {'na': 'a', 'nb': 'b'})
        self.assertRaises(IndexError, args.as_kwargs, 'c', 'd')
        self.assertDictEqual(args.as_kwargs('c'), {'na': 'a', 'nb': 'b', 'nc': 'c'})


class KeywordArgumentsTest(unittest.TestCase):

    defaults = {'kw_a': None, 'kw_b': True}

    def test_initial_kwargs(self):
        kwargs = KeywordArguments(self.defaults, kw_a='A')
        self.assertDictEqual(kwargs, {'kw_a': 'A', 'kw_b': True})

    def test_set_keyword(self):
        kwargs = KeywordArguments(self.defaults, kw_a='A')
        kwargs['kw_b'] = 'B'
        self.assertDictEqual(kwargs, {'kw_a': 'A', 'kw_b': 'B'})
        self.assertRaises(KeyError, kwargs.__setitem__, 'kw_c', 'C')

    def test_update(self):
        kwargs = KeywordArguments(self.defaults, kw_a='A')
        kwargs.update({'kw_b': 'B'})
        self.assertDictEqual(kwargs, {'kw_a': 'A', 'kw_b': 'B'})
        kwargs.update(kw_b='B2')
        self.assertDictEqual(kwargs, {'kw_a': 'A', 'kw_b': 'B2'})
        self.assertRaises(KeyError, kwargs.update, {'kw_c': 'C'})

    def test_clear(self):
        kwargs = KeywordArguments(self.defaults, kw_a='A')
        self.assertDictEqual(kwargs, {'kw_a': 'A', 'kw_b': True})
        kwargs['kw_b'] = 'B'
        self.assertDictEqual(kwargs, {'kw_a': 'A', 'kw_b': 'B'})
        kwargs.clear()
        self.assertDictEqual(kwargs, {'kw_a': 'A', 'kw_b': True})


class PartializeTest(unittest.TestCase):

    def test_version(self):
        self.assertEqual(get_version((1, 2, 3, 'alpha', 1)), '1.2.3a1')
        self.assertEqual(get_version((1, 2, 3, 'beta', 2)), '1.2.3b2')
        self.assertEqual(get_version((1, 2, 3, 'rc', 3)), '1.2.3c3')
        self.assertEqual(get_version((1, 2, 3, 'final', 4)), '1.2.3')

    def test_initial_arg(self):
        partial = multi_arg_func.partial('a')
        self.assertRaises(ArgumentMissing, partial)
        self.assertRaises(ArgumentOverflow, partial, 'b', 'c')
        x = partial('b')
        self.assertEqual(x, ('a', 'b', None, True))
        partial = single_arg_func.partial('a')
        self.assertEqual(partial(), ('a', None, False))

    def test_initial_args(self):
        partial = multi_arg_func.partial('a', 'b')
        self.assertRaises(ArgumentOverflow, partial, 'c')
        x = partial()
        self.assertEqual(x, ('a', 'b', None, True))
        self.assertRaises(ArgumentOverflow, multi_arg_func.partial, 'a', 'b', 'c')

    def test_no_initial_args(self):
        partial = multi_arg_func.partial()
        self.assertRaises(ArgumentMissing, partial)
        x = partial('a', 'b')
        self.assertEqual(x, ('a', 'b', None, True))

    def test_initial_kwargs(self):
        partial = multi_arg_func.partial(kw_a='A')
        x = partial('a', 'b')
        self.assertEqual(x, ('a', 'b', 'A', True))
        self.assertRaises(InvalidKeyword, multi_arg_func.partial, kw_c='C')

    def test_call_kwargs(self):
        partial = multi_arg_func.partial('a', 'b')
        self.assertRaises(InvalidKeyword, partial, kw_c='C')

    def test_overwrite_initial_kwargs(self):
        partial = multi_arg_func.partial(kw_a='A')
        x = partial('a', 'b', kw_a='A2')
        self.assertEqual(x, ('a', 'b', 'A2', True))

    def test_update_args(self):
        partial = multi_arg_func.partial('a', 'b')
        partial.update(a='a2')
        partial.update({'kw_b': 'B'})
        x = partial()
        self.assertEqual(x, ('a2', 'b', None, 'B'))

    def test_set_args(self):
        partial = multi_arg_func.partial()
        partial.a = 'a'
        x = partial('b')
        self.assertEqual(x, ('a', 'b', None, True))
        partial.b = 'b2'
        x = partial()
        self.assertEqual(x, ('a', 'b2', None, True))
        partial.kw_a = 'A'
        x = partial()
        self.assertEqual(x, ('a', 'b2', 'A', True))
        self.assertRaises(TypeError, partial.__setattr__, 'kw_c', 'C')

    def test_get_args(self):
        partial = multi_arg_func.partial('a', kw_a='A')
        self.assertEqual(partial.a, 'a')
        self.assertEqual(partial.kw_a, 'A')
        self.assertEqual(partial.kw_b, True)
        self.assertRaises(AttributeError, getattr, partial, 'c')

    def test_reset(self):
        partial = multi_arg_func.partial('a', kw_a='A')
        partial.update(b='b')
        x = partial()
        self.assertEqual(x, ('a', 'b', 'A', True))
        partial.reset()
        self.assertRaises(ArgumentMissing, partial)
        x = partial('b2', kw_b='B')
        self.assertEqual(x, ('a', 'b2', 'A', 'B'))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
