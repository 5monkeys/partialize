partialize
==========

Like python partial but with change/extend access to args and kwargs.

.. code:: python

    from partialize import partial

    def dummy(a, b, c=None):
        return 'hello world'

    partial_dummy = partial(dummy)
    partial_dummy.a = 1
    partial_dummy.update(b=2)
    partial_dummy()
    partial_dummy(c=3)


Or as a decorator


.. code:: python

    from partialize import partial

    @partial
    def dummy(a, b, c=None):
        return 'hello world'

    partial_dummy = dummy.partial(1)
    partial_dummy.b = 2
    partial_dummy(c=3)
