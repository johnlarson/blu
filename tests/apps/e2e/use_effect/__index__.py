import uuid
from blu import HTMLElement, Ref, client, use_effect, use_ref, use_state
from blu.html import button, div

__client__ = True


def __page__():
    return EffectTest


@client
def EffectTest():
    from js import alert
    from pyscript.ffi import create_proxy

    render_id, rerender = use_state(0)
    print('TYPE:', type(render_id))

    events_ref = use_ref([])

    @use_effect
    def _():
        events_ref[:] = [*events_ref[:], 'SETUP']
        yield
        events_ref[:] = [*events_ref[:], 'TEARDOWN']

    def handle_button_click(e):
        print('Clicked!')
        rerender(render_id + 1)
    
    return (
        button(onClick=handle_button_click)['CLICK!'],
        div(id='events')[','.join(events_ref[:])]
    )
