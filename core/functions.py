from django.db import models
from decimal import Decimal
import math


def remove_zeros(f):
    d = Decimal(str(f));
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()

def any_detail_str(object, attribute, detail=None, multiple=False):
    self_attribute = eval("object."+attribute)
    if self_attribute:
        if detail:
            return eval("object."+attribute+"."+detail)
        else:
            return self_attribute
    else:
        return ''

def round_off(number, ndigits=0):
    return math.floor(number*10**ndigits)/(10**ndigits)

def round_up(number, ndigits=0):
    return math.ceil(number*10**ndigits)/(10**ndigits)

def round_up_decpower(number):
    ndigits = (-1)*math.ceil(math.log10(number))
    return math.ceil(number*10**ndigits)/(10**ndigits)