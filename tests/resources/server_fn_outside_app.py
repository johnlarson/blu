from blu import server

invalid_called = [False]


@server
def invalid():
    invalid_called[0] = True
