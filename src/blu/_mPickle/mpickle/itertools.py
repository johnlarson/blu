"""
This file is based on the itertools module from micropython-lib:
https://github.com/micropython/micropython-lib/blob/01047889eb1acf115424fee293e03769f6916393/python-stdlib/itertools/itertools.py

All functions except `islice` are identical to the original module. The `islice` function has been adapted with some 
improvements:
1. Simplified argument parsing to handle variable-length arguments (start, stop, step) more effectively.
2. Added input validation to raise a ValueError for invalid inputs, such as negative values for start, stop, and step.
3. Introduced support for open-ended slices (stop=None) to allow for infinite iterables.
4. Optimized the iteration process to make the code cleaner and more efficient.

========
License
======== 

MIT License (MIT)

Copyright (c) 2013, 2014 micropython-lib contributors
Copyright (c) 2025 Mattia Antonini (Fondazione Bruno Kessler) m.antonini@fbk.eu
 
This file is based on code originally released under the MIT License by
micropython-lib contributors. Modifications have been made as noted.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


def count(start=0, step=1):
    while True:
        yield start
        start += step


def cycle(p):
    try:
        len(p)
    except TypeError:
        # len() is not defined for this type. Assume it is
        # a finite iterable so we must cache the elements.
        cache = []
        for i in p:
            yield i
            cache.append(i)
        p = cache
    while p:
        yield from p


def repeat(el, n=None):
    if n is None:
        while True:
            yield el
    else:
        for i in range(n):
            yield el


def chain(*p):
    for i in p:
        yield from i


def islice(iterable, *args):
    start = 0
    stop = None
    step = 1
    if len(args) == 1:
        stop = args[0]
    elif len(args) >= 2:
        start = args[0]
        stop = args[1]
        if len(args) == 3:
            step = args[2]
    if start < 0 or (stop is not None and stop < 0) or step <= 0:
        raise ValueError
    #
    indices = count() if stop is None else range(max(start, stop))
    next_i = start
    for i, element in zip(indices, iterable):
        if i == next_i:
            yield element
            next_i += step


def tee(iterable, n=2):
    return [iter(iterable)] * n


def starmap(function, iterable):
    for args in iterable:
        yield function(*args)


def accumulate(iterable, func=lambda x, y: x + y):
    it = iter(iterable)
    try:
        acc = next(it)
    except StopIteration:
        return
    yield acc
    for element in it:
        acc = func(acc, element)
        yield acc
