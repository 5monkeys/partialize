partialize
==========

Like python :code:`functools.partial` but with change/extend access to args and kwargs.
Also a great tool even if no partial is needed but the function takes args/kwargs that often depends on logic.

Easiest used as a decorator

.. code:: python

    from partialize import partialize

    @partialize
    def dummy(a, b, c=None):
        return 'hello world'

    partial_dummy = dummy.partial(1)
    partial_dummy.b = 2
    partial_dummy(c=3)

or invoked inline...

.. code:: python

    partial_dummy = partialize(dummy)
    partial_dummy.a = 1
    partial_dummy.update(b=2)
    partial_dummy()
    partial_dummy(c=3)

Use it on functions that needs logic to affect arguments passed, instead of building and passing a `dict` as kwargs
which often gets quite messy and hard to read.

Dict kwargs example:

.. code:: python

    from partialize import partialize

    @partialize
    def search_products(site, query=None, brand=None, tags=None):
        pass

    kwargs = {}

    if logic:
        kwargs['query'] = q

    if more_logic:
        kwargs['brand'] = 'brand name'

    products = search_products(site, **kwargs)

Partialize example:

.. code:: python

    search = search_products.partial(site)

    if logic:
        search.query = q

    if more_logic:
        search.brand = 'brand name'

    products = search()

..

    **Note:** function argument names are validated when set, unlike dict string keys.
