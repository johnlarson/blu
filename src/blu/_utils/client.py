import platform

is_client: bool = platform.system() == "Emscripten"


class WrongEnvironmentError(Exception):
    pass
