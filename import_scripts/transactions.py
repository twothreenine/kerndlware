# -*- coding: utf-8 -*-

import csv
import datetime
from core import models

print('hello')

with open('import_scripts/transactions.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for index,row in enumerate(reader):
        ttype = row[10]
        print(ttype)
        # print(index)
        # print(type(row[0]))
        # print(', '.join(row))