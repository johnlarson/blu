import blu.html


del_ = getattr(blu.html, 'del')
tag_name_with_dashes = getattr(blu.html, 'tag-name-with-dashes')


def __page__():
    return tag_name_with_dashes[
        del_['Hello, World!'],
    ]