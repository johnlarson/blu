import uuid
from blu import HTMLElement, Ref, client, use_effect, use_ref, use_state
from blu.html import button, div

__client__ = True


def __page__():
    return EffectTest


@client
def EffectTest():
    from js import alert

    render_id, rerender = use_state(0)

    @use_effect
    def _():
        alert('SETUP')
        yield
        alert('TEARDOWN')

    def handle_button_click():
        rerender(render_id + 1)
    
    return button(onClick=handle_button_click)
