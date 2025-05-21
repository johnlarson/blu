import platform


client: bool = platform.system() == 'Emscripten'


class WrongEnvironmentError(Exception):
    pass