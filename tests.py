import unittest
from partialize import partial, ArgumentMissing, ArgumentOverflow, NamedArguments, KeywordArguments


@partial
def dummy(a, b, kw_a=None, kw_b=True):
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


class PartialTest(unittest.TestCase):

    def test_initial_arg(self):
        partial_dummy = dummy.partial('a')
        self.assertRaises(ArgumentMissing, partial_dummy)
        self.assertRaises(ArgumentOverflow, partial_dummy, 'b', 'c')
        x = partial_dummy('b')
        self.assertEqual(x, ('a', 'b', None, True))

    def test_initial_args(self):
        partial_dummy = dummy.partial('a', 'b')
        self.assertRaises(ArgumentOverflow, partial_dummy, 'c')
        x = partial_dummy()
        self.assertEqual(x, ('a', 'b', None, True))

    def test_no_initial_args(self):
        partial_dummy = dummy.partial()
        self.assertRaises(ArgumentMissing, partial_dummy)
        x = partial_dummy('a', 'b')
        self.assertEqual(x, ('a', 'b', None, True))

    def test_initial_kwargs(self):
        partial_dummy = dummy.partial(kw_a='A')
        x = partial_dummy('a', 'b')
        self.assertEqual(x, ('a', 'b', 'A', True))

    def test_overwrite_initial_kwargs(self):
        partial_dummy = dummy.partial(kw_a='A')
        x = partial_dummy('a', 'b', kw_a='A2')
        self.assertEqual(x, ('a', 'b', 'A2', True))

    def test_update_args(self):
        partial_dummy = dummy.partial('a', 'b')
        partial_dummy.update(a='a2')
        partial_dummy.update({'kw_b': 'B'})
        x = partial_dummy()
        self.assertEqual(x, ('a2', 'b', None, 'B'))

    def test_set_args(self):
        partial_dummy = dummy.partial()
        partial_dummy.a = 'a'
        x = partial_dummy('b')
        self.assertEqual(x, ('a', 'b', None, True))
        partial_dummy.b = 'b2'
        x = partial_dummy()
        self.assertEqual(x, ('a', 'b2', None, True))
        partial_dummy.kw_a = 'A'
        x = partial_dummy()
        self.assertEqual(x, ('a', 'b2', 'A', True))

    def test_get_args(self):
        partial_dummy = dummy.partial('a', kw_a='A')
        self.assertEqual(partial_dummy.a, 'a')
        self.assertEqual(partial_dummy.kw_a, 'A')
        self.assertEqual(partial_dummy.kw_b, True)
        self.assertRaises(AttributeError, getattr, partial_dummy, 'c')

    def test_reset(self):
        partial_dummy = dummy.partial('a', kw_a='A')
        partial_dummy.update(b='b')
        x = partial_dummy()
        self.assertEqual(x, ('a', 'b', 'A', True))
        partial_dummy.reset()
        self.assertRaises(ArgumentMissing, partial_dummy)
        x = partial_dummy('b2', kw_b='B')
        self.assertEqual(x, ('a', 'b2', 'A', 'B'))
