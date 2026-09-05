import sys

is_client: bool

if sys.implementation.name == "micropython":
    is_client = True
else:
    import platform

    is_client = platform.system() == "Emscripten"
