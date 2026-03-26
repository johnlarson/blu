from pathlib import Path

from blu import server

value = ["UNTOUCHED"]


@server
def change_file_contents():
    value[0] = "CHANGED"
