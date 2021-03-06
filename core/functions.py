from django.db import models
from decimal import Decimal
import math
from collections import Counter
import datetime
from core.config import *

def remove_zeros(f):
    d = Decimal(str(f));
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()

def any_detail_str(object, attribute, detail=None, multiple=False):
    obj_attribute = eval("object."+attribute)
    if obj_attribute:
        if detail:
            return eval("object."+attribute+"."+detail)
        else:
            return obj_attribute
    else:
        return ''

def round_off(number, ndigits=0):
    return math.floor(number*10**ndigits)/(10**ndigits)

def round_up(number, ndigits=0):
    return math.ceil(number*10**ndigits)/(10**ndigits)

def round_up_decpower(number):
    ndigits = (-1)*math.ceil(math.log10(number))
    return math.ceil(number*10**ndigits)/(10**ndigits)

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)

def list_str(my_list, sorted_by_attribute=None, descending=True, displayed_attribute="name", type_plural="", elements=2):
    """
    Returns a string from a list of strings like "x, y, and n-2 other [type]s" or "n [type]s".
    If the list consists of objects, they can be sorted by one of their attributes given as sorted_by_attribute;
    and to represent them by a different attribute than their name, you can give that attribute as displayed_attribute.
    We need to know how to call the list elements in plural. You can give that plural manually as type_plural; else, for objects, this function will get the class name and append an "s".
    The parameter "elements" sets a maximum of objects to be written, including the "and n others". Use elements=0 to write them all without maximum.
    """
    count = len(my_list)

    if not count:
        if type_plural == "":
            return "None"
        else:
            return "No "+type_plural

    else:
        if type_plural == "":
            objects = " "+str(my_list[0].__class__.__name__).lower()+"s" # TODO: only if list contains objects, not strings etc; otherwise just use "s" for "others"
        else:
            objects = " "+type_plural

        if count == 1:
            return str(eval("my_list[0]."+displayed_attribute))

        elif elements == 1:
            return str(count)+" "+objects

        else:
            if sorted_by_attribute:
                my_list = sorted(my_list, key=lambda t: eval("t."+sorted_by_attribute), reverse=descending)
            obj_names = str(eval("my_list[0]."+displayed_attribute)) # writes first element into string
            my_list.pop(0) # removes that first element
            elements_written = 1
            for obj in my_list:
                if elements_written == elements-1 or elements_written == count-1:
                    break
                obj_names += ", " + str(eval("obj."+displayed_attribute))
                elements_written += 1
            left_to_write = count - elements_written
            if count > 2 and (elements > 2 or elements == 0):
                obj_names += "," # Last comma before 'and'. Replace this with a variable for multilingual support which can be "," or ""
            if left_to_write == 1:
                obj_names += " and "+str(eval("my_list[-1]."+displayed_attribute))
            else:
                obj_names += " and "+str(left_to_write)+" other"+objects
            return obj_names

def calc_next_date(obj):
    if obj.day_specified and obj.time_period.is_month:
        if obj.next_performance.day > 28:
            obj.next_performance.replace(day=28)
        new_month = obj.next_performance.month+obj.time_period_multiplicator
        new_year = obj.next_performance.year
        while new_month > 12:
            new_year += 1
            new_month -= 12
        return obj.next_performance.replace(year=new_year, month=new_month)
    elif obj.day_specified and obj.time_period.is_year:
        if obj.next_performance.day > 28:
            obj.next_performance.replace(day=28)
        return obj.next_performance.replace(year=obj.next_performance.year+obj.time_period_multiplicator)
    else:
        return obj.next_performance + datetime.timedelta(days=obj.time_period.days*obj.time_period_multiplicator)

def date_format(user=None, style='short'):
    if style == 'short':
        if user:
            if user.short_date_format:
                return user.short_date_format
            else:
                return get_config("short_date_format")
        else:
            return get_config("short_date_format")
    elif style == 'long':
        if user:
            if user.long_date_format:
                return user.long_date_format
            else:
                return get_config("long_date_format")
        else:
            return get_config("long_date_format")

def bootstrap_date_format(date_format):
    return date_format.replace('%a', 'D').replace('%A', 'DD').replace('%b', 'M').replace('%B', 'MM').replace('%d', 'dd').replace('%m', 'mm').replace('%y', 'yy').replace('%Y', 'yyyy')