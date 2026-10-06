class _TypeStub:
    __slots__ = ()

    def __repr__(self):
        return "TypeStub"

    def __getitem__(self, item):
        return self

    def __or__(self, other):
        return self

    def __ror__(self, other):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class NoopClass:
    pass


class _TypeClassStub:
    """Metaclass so stub types support ``X | Y`` on runtimes without PEP 604."""

    def __or__(cls, other):
        return _TypeStub()

    def __ror__(cls, other):
        return _TypeStub

    def __getitem__(cls, item):
        return cls

    def __mro_entries__(self, bases):
        return (NoopClass,)


def type_import(scope, type_stub_names, type_class_stub_names):
    for type_stub_name in type_stub_names:
        scope[type_stub_name] = _TypeStub()
    for type_class_stub_name in type_class_stub_names:
        scope[type_class_stub_name] = _TypeClassStub()


def import_module(module_name):
    return __import__(module_name, None, None, ("*",))


def mapping_combine(*mappings):
    ret = {}
    for m in mappings:
        for k, v in m.items():
            ret[k] = v
    return ret


def tuple_combine(*iterables):
    ret = ()
    for i in iterables:
        ret += i
    return ret


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def is_generator(obj):
    return (
        is_iterable(obj)
        and hasattr(obj, "__next__")
        and hasattr(obj, "send")
        and hasattr(obj, "throw")
        and hasattr(obj, "close")
    )


def is_async_generator(obj):
    return (
        hasattr(obj, "__aiter__")
        and hasattr(obj, "__anext__")
        and hasattr(obj, "asend")
        and hasattr(obj, "athrow")
        and hasattr(obj, "aclose")
    )


def is_coroutine(obj):
    return (
        hasattr(obj, "__await__")
        and hasattr(obj, "send")
        and hasattr(obj, "throw")
        and hasattr(obj, "close")
    )


try:
    from pyodide.ffi import create_proxy

    is_pyodide = True
except ImportError:

    def create_proxy(obj):
        return obj

    is_pyodide = False
