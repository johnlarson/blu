from blu.html import p


def __page__(employee_id, date):
    return p[f'This is employee #{employee_id}\'s time card for {date}.']