from django.test import TestCase
from .models import *

# Create your tests here.

class AccountTableTest(TestCase):
    def test_init(self):
        account_table = AccountTable(1)
        dim = account_table.get_dimensions()
        for i in range(0, dim[0]):
            for j in range(0, dim[1]):
                print(account_table.get(i, j))