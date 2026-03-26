from pathlib import Path

from blu import server


@server
def change_file_contents():
    path = Path(__file__).parent / "file.txt"
    with open(path, "w") as f:
        f.write("CHANGED")
