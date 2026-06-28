import math

def round_125(value):
    exponent = math.floor(math.log10(value))
    base = value / (10 ** exponent)

    if base <= 1:
        nice = 1
    elif base <= 2:
        nice = 2
    elif base <= 5:
        nice = 5
    else:
        nice = 10

    return nice * (10 ** exponent)


def calc_scale(value):
    raw = abs(value) / 4
    return round_125(raw)
