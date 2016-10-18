from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class PercentField(models.FloatField):
    """
    Float field that ensures field value is in the range 0-100.
    """
    default_validators = [
        MinValueValidator(0),
        MaxValueValidator(100),
    ]