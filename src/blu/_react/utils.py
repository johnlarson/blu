import re


def py_to_html_name(py_name: str) -> str:
    return re.sub('_$', '', py_name).replace('_', '-')