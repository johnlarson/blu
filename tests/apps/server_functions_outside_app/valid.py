from blu import server


valid_called = [False]


@server
def valid():
    valid_called[0] = True
