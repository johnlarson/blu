def __page__():
    from js import window
    from pyscript.ffi import create_proxy

    return div(id='status')['Success!']