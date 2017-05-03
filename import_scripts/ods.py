# -*- coding: utf-8 -*-

import csv
import datetime
from core import models

"""
Questions:
- we have to detect whether the next row is of type 9 (exception) resp. how many of the following rows are of type 9
- Special characters like umlaute and ß are ignored with errors='ignore', how can we read them?
"""

def import_products(import_inactive_products=True):
    """
    products_basic is the csv from Eingabetabelle Bedarfsschätzung; products_extended is from Bestellrechner.Rech
    """
    with open('import_scripts/products_basic.csv', newline='', encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for index,row in enumerate(reader):
            if not row[1] == '':
                if import_inactive_products == True or row[0] == '1':
                    name = row[2]
                    if not row[3] == '' and not row[4] == '':
                        description = row[3] + '; ' + row[4]
                    else:
                        description = row[3] + row[4]
                    if row[0] == '1':
                        active = True
                    else:
                        active = False
                    try:
                        unit = models.Unit.objects.get(abbr=row[6]) # shouldn't require exact match, compare names
                    except models.Unit.DoesNotExist:
                        unit = models.Unit(full_name='', abbr=row[6], weight=row[14], continuous=True)
                        unit.save()
                    if not row[5] == '':
                        presumed_price = float(row[5].replace(',', '.')[0:-2])
                    else:
                        presumed_price = None
                    original_id = int(row[1])
                    p = models.Product(name=name, description=description, active=active, unit=unit, presumed_price=presumed_price, original_id=original_id)
                    p.save()
    with open('import_scripts/products_extended.csv', newline='', encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for index,row in enumerate(reader):
            if not row[1] == '':
                if import_inactive_products == True or row[0] == '1':
                    p = models.Product.objects.get(original_id=reader.line_num) # row index of current row?
                    if not row[10] == '':
                        p.storability = float(row[10])*30.4
                    else:
                        p.storability = None
                    p.save()

def import_suppliers():
    with open('import_scripts/suppliers.csv', newline='', encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for index,row in enumerate(reader):
            if not row[18] == '':
                name = row[19]
                min_interval = float(row[20].replace(',', '.')) * 30.4
                # original_id = int(row[18])
                s = models.Supplier(name=name, min_interval=min_interval)
                s.save()

def import_accounts(create_users=True):
    with open('import_scripts/accounts.csv', newline='', encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for index,row in enumerate(reader):
            if not row[0] == '':
                original_id = int(row[0])
                name = row[2]
                if row[4] == '':
                    active = True
                else:
                    active = False
                a = models.Account(name=name, original_id=original_id, active=active)
                a.save()
                comment = row[7]
                if not row[3] == '':
                    rate = int(row[3])
                    if row[5]:
                        start_date = datetime.datetime.strptime(row[5], '%d.%m.%y') # must begin at first day of the month!
                    else:
                        start_date = None
                    if row[6]:
                        end_date = datetime.datetime.strptime(row[6], '%d.%m.%y') # must end at first day of the next month, unless the date is on the 1st, then on this date
                    else:
                        end_date = None
                    ap = models.AccPayPhase(account=a, start=start_date, end=end_date, rate=rate, comment=comment)
                    ap.save()
                if create_users == True:
                    if original_id == 1 or original_id == 52: # specifically for our database with Spontankäufer and Spendenkonto
                        u = models.VirtualUser(name=name, active=active, comment=comment)
                        u.save()
                    else:
                        u = models.Person(name=name, active=active, comment=comment)
                        u.save()
                        n = re.search('(.+ ?.+) (.+)', name) # improve regex code: if there is only one word, group 2 shall be empty (first name only)
                        if n:
                            u.first_name = n.group(1)
                            u.last_name = n.group(2)
                    u.accounts.add(a)
                    u.save()
                    a.users.add(u)
                    a.save()

def import_batches(owner_id=None):
    with open('import_scripts/batches.csv', newline='', encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for index,row in enumerate(reader):
            if not row[11] == '' and not row[13] == '':
                name = row[12]
                comment = row[10]
                product = models.Product.objects.get(original_id=int(row[1]))
                try:
                    supplier = models.Supplier.objects.get(name=row[9]) # shouldn't require exact match, compare names
                except models.Supplier.DoesNotExist:
                    supplier = models.Supplier(name=row[9])
                    supplier.save()
                try:
                    unit = models.Unit.objects.get(abbr=row[13]) # shouldn't require exact match, compare names
                except models.Unit.DoesNotExist:
                    unit = models.Unit(full_name='', abbr=row[13], weight=row[14], continuous=True)
                    unit.save()
                price = 0
                if not row[3] == '':
                    price = float(row[3].replace(',', '.')[0:-2])
                production_date = None
                if not row[2] == '':
                    production_date = datetime.datetime.strptime(row[2], '%d.%m.%y')
                date_of_expiry = None
                if not row[8] == '':
                    date_of_expiry = datetime.datetime.strptime(row[8], '%d.%m.%y')
                special_density = 0
                if not row[5] == '':
                    special_density = float(row[5])
                original_id = int(row[11])
                owner = None
                if not owner_id == None:
                    owner = models.Account.objects.get(pk=owner_id)
                b = models.Batch(name=name, comment=comment, consumable=product, supplier=supplier, unit=unit, price=price, production_date=production_date, date_of_expiry=date_of_expiry, special_density=special_density, original_id=original_id)
                b.save()

def import_transactions(user_id, currency1_id=1, money_box_id=1):
    with open('import_scripts/transactions.csv', newline='', encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for index,row in enumerate(reader):
            original_ttype = int(row[10])
            if not row[7] == '' and original_ttype >= 1 and original_ttype <= 10 and not original_ttype == 9:
                originator_account = models.Account.objects.get(original_id=int(row[7]))
                user = models.User.objects.get(pk=user_id)
                date = datetime.datetime.strptime(row[9], '%d.%m.%y')
                # entry_date = datetime.date.today()
                amount = float(row[4].replace(',', '.'))
                comment = row[6]
                value = row[24]
                if not value:
                    value = row[25]
                value = float(value.replace('.', '').replace(',', '.')[0:-2])
                # status = models.ForeignKey('TransactionStatus', blank=True, null=True)
                original_batch = int(row[17])

                ttype = None
                if original_ttype == 1 and original_batch <= 3: # depositation
                    ttype = 4
                if original_ttype == 1 and original_batch >= 4: # depositation by insertion of goods
                    ttype = 40
                if original_ttype == 2 and original_batch <= 3: # inpayment
                    ttype = 3
                if original_ttype == 2 and original_batch >= 3: # inpayment by insertion of goods
                    ttype = 12
                if original_ttype == 3 and original_batch <= 3: # payout of balance
                    ttype = 5
                if original_ttype == 3 and original_batch >= 3: # taking
                    ttype = 1
                if original_ttype == 4 and original_batch <= 3: # payout of deposit
                    ttype = 6
                if original_ttype == 4 and original_batch >= 3: # payout of deposit as goods
                    ttype = 60
                if original_ttype == 5: # costsharing
                    ttype = 8
                if original_ttype == 6: # proceedssharing
                    ttype = 9
                if original_ttype == 7: # recovery
                    ttype = 11
                if original_ttype == 8: # donation
                    ttype = 10
                if original_ttype == 10: # transfer
                    ttype = 7

                if ttype == 1: # taking
                    batch = models.Batch.objects.get(original_id=original_batch)
                    t = models.Taking(originator_account=originator_account, entered_by_user=user, date=date, amount=amount, comment=comment, batch=batch)
                    t.save()
                    t.perform()

                if ttype == 2: # Restitution (currently not in use)
                    batch = models.Batch.objects.get(original_id=original_batch)
                    t = models.Restitution(originator_account=originator_account, entered_by_user=user, date=date, amount=amount, comment=comment, batch=batch)
                    t.save()
                    t.perform()

                if ttype == 3: # inpayment
                    currency = models.Currency.objects.get(pk=currency1_id)
                    money_box = models.MoneyBox.objects.get(pk=money_box_id)
                    t = models.Inpayment(originator_account=originator_account, entered_by_user=user, date=date, amount=amount, comment=comment, currency=currency, money_box=money_box, confirmed_by=user, confirmation_comment="imported automatically")
                    t.save()
                    t.perform()

                if ttype == 4: # depositation
                    currency = models.Currency.objects.get(pk=currency1_id)
                    money_box = models.MoneyBox.objects.get(pk=money_box_id)
                    t = models.Depositation(originator_account=originator_account, entered_by_user=user, date=date, amount=amount, comment=comment, currency=currency, money_box=money_box, confirmed_by=user, confirmation_comment="imported automatically")
                    t.save()
                    t.perform()

                if ttype == 5: # PayOutBalance
                    currency = models.Currency.objects.get(pk=currency1_id)
                    money_box = models.MoneyBox.objects.get(pk=money_box_id)
                    t = models.PayOutBalance(originator_account=originator_account, entered_by_user=user, date=date, amount=amount, comment=comment, currency=currency, money_box=money_box, confirmed_by=user, confirmation_comment="imported automatically")
                    t.save()
                    t.perform()

                if ttype == 6: # PayOutDeposit
                    currency = models.Currency.objects.get(pk=currency1_id)
                    money_box = models.MoneyBox.objects.get(pk=money_box_id)
                    t = models.PayOutDeposit(originator_account=originator_account, entered_by_user=user, date=date, amount=amount, comment=comment, currency=currency, money_box=money_box, confirmed_by=user, confirmation_comment="imported automatically")
                    t.save()
                    t.perform()

                if ttype == 7: # Transfer
                    recipient_account = models.Account.objects.get(original_id=int(row[5]))
                    t = models.Transfer(originator_account=originator_account, entered_by_user=user, date=date, amount=value, comment=comment, recipient_account=recipient_account)
                    t.save()
                    t.perform()

                if ttype == 8: # CostSharing
                    participating_accounts = models.Account.objects.all() # tODO: minus exceptions
                    t = models.CostSharing(originator_account=originator_account, entered_by_user=user, date=date, amount=value, comment=comment, approved_by=user, approval_comment="imported automatically")
                    t.save()
                    t.perform(transaction_type_id=8, participating_accounts=participating_accounts)

                if ttype == 9: # ProceedsSharing
                    participating_accounts = models.Account.objects.all()
                    t = models.ProceedsSharing(originator_account=originator_account, entered_by_user=user, date=date, amount=value, comment=comment, approved_by=user, approval_comment="imported automatically")
                    t.save()
                    t.perform(transaction_type_id=9, participating_accounts=participating_accounts)

                if ttype == 10: # Recovery
                    participating_accounts = models.Account.objects.all()
                    t = models.Recovery(originator_account=originator_account, entered_by_user=user, date=date, amount=value, comment=comment, approved_by=user, approval_comment="imported automatically")
                    t.save()
                    t.perform(transaction_type_id=10, participating_accounts=participating_accounts)

                if ttype == 11: # Donation
                    participating_accounts = models.Account.objects.all()
                    t = models.Donation(originator_account=originator_account, entered_by_user=user, date=date, amount=value, comment=comment, approved_by=user, approval_comment="imported automatically")
                    t.save()
                    t.perform(transaction_type_id=11, participating_accounts=participating_accounts)

                # to be implemented: ttype 12, 40, 60

            

            # print(index)
            # print(type(row[0]))
            # print(', '.join(row))