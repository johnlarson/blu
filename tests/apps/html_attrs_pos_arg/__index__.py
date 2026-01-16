from blu.html import form, input, label


def __page__():
    return form[
        label({'for': 'value-input'})['Value:'],
        input({'data-value': '23'}, id='value-input'),
    ]