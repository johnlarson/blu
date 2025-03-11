from blu.html import div

original = div(className='my-div')['A', 'B']


def __page__():
    return original['C', 'D']