from blu import server

value = ["UNTOUCHED"]


@server
def set_value(new_value):
    value[0] = new_value
