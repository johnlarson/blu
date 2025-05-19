import platform


client = platform.system() == 'Emscripten'


class WrongEnvironmentError(Exception):
    pass