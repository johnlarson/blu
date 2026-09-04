import importlib


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


class _TypeClassStubMeta(type):
    """Metaclass so stub types support ``X | Y`` on runtimes without PEP 604."""

    def __or__(cls, other):
        return _TypeStub()

    def __ror__(cls, other):
        return _TypeStub


class _TypeClassStub(metaclass=_TypeClassStubMeta):
    __slots__ = ()

    def __class_getitem__(cls, item):
        return cls


def type_import(module_name, scope, type_stub_names, type_class_stub_names):
    try:
        _import_all(module_name, scope)
    except ImportError:
        for type_stub_name in type_stub_names:
            scope[type_stub_name] = _TypeStub()
        for type_class_stub_name in type_class_stub_names:
            scope[type_class_stub_name] = _TypeClassStub()
        return True
    return False


def _import_all(module_name, scope):
    module = importlib.import_module(module_name)
    scope.update({k: v for k, v in module.__dict__.items() if not k.startswith("_")})
