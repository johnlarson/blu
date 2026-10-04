from blu import client, use_effect, use_ref, use_state
from blu.html import button, div

from logging import getLogger

log = getLogger("blu")

__client__ = True


def __page__():
    return EffectTest


@client
def EffectTest():

    render_id, rerender = use_state(0)

    events_ref = use_ref([])

    @use_effect
    def _():
        events_ref[:] = events_ref[:] + ["SETUP"]
        log.debug("Called use_effect callback in use_effect test.")
        yield
        events_ref[:] = events_ref[:] + ["TEARDOWN"]

    def handle_button_click(e):
        log.debug("Handling button click...")
        rerender(render_id + 1)

    return (
        button(onClick=handle_button_click)["CLICK!"],
        div(id="events")[",".join(events_ref[:])],
    )
