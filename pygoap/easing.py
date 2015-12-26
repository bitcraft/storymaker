"""
The `progress` parameter in each function is in the range 0-1.
"""
from math import sqrt, cos, sin, pi


def linear(progress):
    return progress


def in_quad(progress):
    return progress * progress


def out_quad(progress):
    return -1.0 * progress * (progress - 2.0)


def in_out_quad(progress):
    p = progress * 2
    if p < 1:
        return 0.5 * p * p
    p -= 1.0
    return -0.5 * (p * (p - 2.0) - 1.0)


def in_cubic(progress):
    return progress * progress * progress


def out_cubic(progress):
    p = progress - 1.0
    return p * p * p + 1.0


def in_out_cubic(progress):
    p = progress * 2
    if p < 1:
        return 0.5 * p * p * p
    p -= 2
    return 0.5 * (p * p * p + 2.0)


def in_quart(progress):
    return progress * progress * progress * progress


def out_quart(progress):
    p = progress - 1.0
    return -1.0 * (p * p * p * p - 1.0)


def in_out_quart(progress):
    p = progress * 2
    if p < 1:
        return 0.5 * p * p * p * p
    p -= 2
    return -0.5 * (p * p * p * p - 2.0)


def in_quint(progress):
    return progress * progress * progress * progress * progress


def out_quint(progress):
    p = progress - 1.0
    return p * p * p * p * p + 1.0


def in_out_quint(progress):
    p = progress * 2
    if p < 1:
        return 0.5 * p * p * p * p * p
    p -= 2.0
    return 0.5 * (p * p * p * p * p + 2.0)


def in_sine(progress):
    return -1.0 * cos(progress * (pi / 2.0)) + 1.0


def out_sine(progress):
    return sin(progress * (pi / 2.0))


def in_out_sine(progress):
    return -0.5 * (cos(pi * progress) - 1.0)


def in_expo(progress):
    if progress == 0:
        return 0.0
    return pow(2, 10 * (progress - 1.0))


def out_expo(progress):
    if progress == 1.0:
        return 1.0
    return -pow(2, -10 * progress) + 1.0


def in_out_expo(progress):
    if progress == 0:
        return 0.0
    if progress == 1.:
        return 1.0
    p = progress * 2
    if p < 1:
        return 0.5 * pow(2, 10 * (p - 1.0))
    p -= 1.0
    return 0.5 * (-pow(2, -10 * p) + 2.0)


def in_circ(progress):
    return -1.0 * (sqrt(1.0 - progress * progress) - 1.0)


def out_circ(progress):
    p = progress - 1.0
    return sqrt(1.0 - p * p)


def in_out_circ(progress):
    p = progress * 2
    if p < 1:
        return -0.5 * (sqrt(1.0 - p * p) - 1.0)
    p -= 2.0
    return 0.5 * (sqrt(1.0 - p * p) + 1.0)


def in_elastic(progress):
    p = .3
    s = p / 4.0
    q = progress
    if q == 1:
        return 1.0
    q -= 1.0
    return -(pow(2, 10 * q) * sin((q - s) * (2 * pi) / p))


def out_elastic(progress):
    p = .3
    s = p / 4.0
    q = progress
    if q == 1:
        return 1.0
    return pow(2, -10 * q) * sin((q - s) * (2 * pi) / p) + 1.0


def in_out_elastic(progress):
    p = .3 * 1.5
    s = p / 4.0
    q = progress * 2
    if q == 2:
        return 1.0
    if q < 1:
        q -= 1.0
        return -.5 * (pow(2, 10 * q) * sin((q - s) * (2.0 * pi) / p))
    else:
        q -= 1.0
        return pow(2, -10 * q) * sin((q - s) * (2.0 * pi) / p) * .5 + 1.0


def in_back(progress):
    return progress * progress * ((1.70158 + 1.0) * progress - 1.70158)


def out_back(progress):
    p = progress - 1.0
    return p * p * ((1.70158 + 1) * p + 1.70158) + 1.0


def in_out_back(progress):
    p = progress * 2.
    s = 1.70158 * 1.525
    if p < 1:
        return 0.5 * (p * p * ((s + 1.0) * p - s))
    p -= 2.0
    return 0.5 * (p * p * ((s + 1.0) * p + s) + 2.0)


def _out_bounce_internal(t, d):
    p = t / d
    if p < (1.0 / 2.75):
        return 7.5625 * p * p
    elif p < (2.0 / 2.75):
        p -= (1.5 / 2.75)
        return 7.5625 * p * p + .75
    elif p < (2.5 / 2.75):
        p -= (2.25 / 2.75)
        return 7.5625 * p * p + .9375
    else:
        p -= (2.625 / 2.75)
        return 7.5625 * p * p + .984375


def _in_bounce_internal(t, d):
    return 1.0 - _out_bounce_internal(d - t, d)


def in_bounce(progress):
    return _in_bounce_internal(progress, 1.)


def out_bounce(progress):
    return _out_bounce_internal(progress, 1.)


def in_out_bounce(progress):
    p = progress * 2.
    if p < 1.:
        return _in_bounce_internal(p, 1.) * .5
    return _out_bounce_internal(p - 1., 1.) * .5 + .5

