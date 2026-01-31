from blu import client, use_state
from blu.html import button, div

__client__ = True


def __page__():
    return StateTest


@client
def StateTest():
    count, set_count = use_state(0)

    def click_increment(e):
        set_count(count + 1)
    
    return (
        div(id='count')[count],
        button(id='increment', onClick=click_increment)['Increment'],
    )