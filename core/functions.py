from django.db import models
from decimal import Decimal


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