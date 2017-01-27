from django.db import models
from django.db.models import Q
import datetime
from .fields import PercentField
import datetime
import itertools
from .models import *

class BatchTransactionTable:
    def __init__(self, batch_id):
        self.batch_id = batch_id
        self.rows = list()
        self.generate()

    def generate(self):
        takings = Taking.objects.filter(batch=self.batch_id)
        restitutions = Restitution.objects.filter(batch=self.batch_id)
        # cost_sharings = CostSharing.objects.all()
        # proceeds_sharings = ProceedsSharing.objects.all()
        # donations = Donation.objects.all()
        # recoveries = Recovery.objects.all()
        transactions = sorted(list(itertools.chain(takings, restitutions)), key=lambda t: (t.date, t.id))
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            row = list()
            row.append(transaction.id)
            row.append(transaction.date)
            row.append(transaction.matter_str(account=0, show_contents=False, show_batch=False))
            row.append(transaction.entry_details_str)
            row.append(transaction.value_str(account=0))
            row.append(transaction.batch_stock_str())
            row.append(transaction.comment_str)
            self.rows.append(row)

class ConsumableTransactionTable:
    def __init__(self, consumable_id):
        self.consumable_id = consumable_id
        consumable = Consumable.objects.get(pk=consumable_id)
        batches = Batch.objects.filter(consumable=consumable)
        self.rows = list()
        self.generate()

    def generate(self):
        # takings = []
        # for t in Taking.objects.all():
        #     if t.originator_account == acc or cs.participating_accounts.filter(pk=self.account_id).count():
        #         cost_sharings.append(cs)
        takings = Taking.objects.filter(batch__consumable=self.consumable_id)
        restitutions = Restitution.objects.filter(batch__consumable=self.consumable_id)
        # cost_sharings = CostSharing.objects.all()
        # proceeds_sharings = ProceedsSharing.objects.all()
        # donations = Donation.objects.all()
        # recoveries = Recovery.objects.all()
        transactions = sorted(list(itertools.chain(takings, restitutions)), key=lambda t: (t.date, t.id))
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            row = list()
            row.append(transaction.id)
            row.append(transaction.date)
            row.append(transaction.matter_str(account=0))
            row.append(transaction.entry_details_str)
            row.append(transaction.value_str(account=0))
            row.append(transaction.consumable_stock_str())
            row.append(transaction.comment_str)
            self.rows.append(row)

class TransactionTable:
    def __init__(self):
        self.rows = list()
        self.generate()

    def generate(self):
        takings = Taking.objects.all()
        restitutions = Restitution.objects.all()
        inpayments = Inpayment.objects.all()
        depositations = Depositation.objects.all()
        transfers = Transfer.objects.all()
        cost_sharings = CostSharing.objects.all()
        proceeds_sharings = ProceedsSharing.objects.all()
        donations = Donation.objects.all()
        recoveries = Recovery.objects.all()
        transactions = sorted(list(itertools.chain(takings, restitutions, inpayments, depositations, transfers, cost_sharings, proceeds_sharings, donations, recoveries)), key=lambda t: (t.date, t.id))
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            row = list()
            row.append(transaction.id)
            row.append(transaction.date)
            row.append(transaction.matter_str(account=0))
            row.append(transaction.entry_details_str)
            row.append(transaction.value_str(account=0))
            row.append(transaction.comment_str)
            self.rows.append(row)

class AccountTable:
    def __init__(self, account_id, types, start_date, end_date, enterer):
        self.account_id = account_id
        self.types = types
        self.start_date = start_date
        self.end_date = end_date
        self.enterer = enterer
        self.rows = list()
        self.generate()

    def generate(self):
        acc = Account.objects.get(pk=self.account_id)
        takings = Taking.objects.filter(originator_account=self.account_id)
        restitutions = Restitution.objects.filter(originator_account=self.account_id)
        inpayments = Inpayment.objects.filter(originator_account=self.account_id)
        depositations = Depositation.objects.filter(originator_account=self.account_id)
        transfers = Transfer.objects.filter(Q(originator_account=self.account_id) | Q(recipient_account=self.account_id))
        cost_sharings = []
        for cs in CostSharing.objects.all():
            if cs.originator_account == acc or cs.participating_accounts.filter(pk=self.account_id).count():
                cost_sharings.append(cs)
        # cost_sharing = CostSharing.objects.filter(originator_account=self.account_id) | CostSharing.objects.filter(participating_accounts=self.account_id)
        proceeds_sharings = []
        for ps in ProceedsSharing.objects.all():
            if ps.originator_account == acc or ps.participating_accounts.filter(pk=self.account_id).count():
                proceeds_sharings.append(ps)
        # proceeds_sharing = ProceedsSharing.objects.filter(originator_account=self.account_id) | ProceedsSharing.objects.filter(participating_accounts=self.account_id)
        donations = []
        for dt in Donation.objects.all():
            if dt.originator_account == acc or dt.participating_accounts.filter(pk=self.account_id).count():
                donations.append(ps)
        # donation = Donation.objects.filter(originator_account=self.account_id) & Donation.objects.filter(participating_accounts=self.account_id)
        recoveries = []
        for rc in Recovery.objects.all():
            if rc.originator_account == acc or rc.participating_accounts.filter(pk=self.account_id).count():
                recoveries.append(ps)
        # recovery = Recovery.objects.filter(originator_account=self.account_id) & Recovery.objects.filter(participating_accounts=self.account_id)
        all_transactions = sorted(list(itertools.chain(takings, restitutions, inpayments, depositations, transfers, cost_sharings, proceeds_sharings, donations, recoveries)), key=lambda t: (t.date, t.id))
        transactions = []
        for tr in all_transactions:
            if self.start_date == None:
                start_condition = True
            else:
                if tr.date >= self.start_date:
                    start_condition = True
                else:
                    start_condition = False
            if self.end_date == None:
                end_condition = True
            else:
                if tr.date <= self.end_date:
                    end_condition = True
                else:
                    end_condition = False
            if self.enterer == None:
                enterer_condition = True
            elif self.enterer == tr.entered_by_user:
                enterer_condition = True
            else:
                enterer_condition = False
            if tr.transaction_type in self.types and start_condition == True and end_condition == True and enterer_condition == True:
                transactions.append(tr)
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            row = list()
            row.append(transaction.id)
            row.append(transaction.date)
            row.append(transaction.matter_str(account=self.account_id))
            row.append(transaction.entry_details_str)
            row.append(transaction.value_str(account=self.account_id))
            row.append(transaction.balance_str(account=self.account_id))
            row.append(transaction.comment_str)
            self.rows.append(row)

    # def get(self, row_index, column_index):
    #    return self.rows[row_index][column_index]

    def get_dimensions(self):
        return (len(self.rows), 7) # where is this used ???

class TrDetailsTable:
# Creates a table to show details to a transaction, such as the ID and, in case of cost sharing etc., the individual shares
    def __init__(self, transaction):
        transaction = transaction
        self.rows = list()
        self.generate()

    def generate(self):
        shares = sorted(Charge.objects.filter(transaction=transaction), key=lambda t: t.transaction.id).remove()
        row = list()
        row.append("Tr No. " + transaction.id)
        if CostSharing.objects.get(id=transaction.id).count() or ProceedsSharing.objects.get(id=transaction.id).count() or Donation.objects.get(id=transaction.id).count() or Recovery.objects.get(id=transaction.id).count():
            self.rows.append(row) # Head line of the table
            row.append("Total: " + shares.count() + " participants")
            total_rate = 0
            total_value = 0
            for charge in shares:
                total_rate += charge.account.calc_rate(date=transaction.date)
                total_value += charge.value
            row.append(total_rate + "x")
            row.append(total_value + " €")
            self.rows.append(row)
            for i in range(0, len(shares)):
                row.append(charge.account.name)
                row.append(charge.account.calc_rate(date=transaction.date) + "x")
                row.append(charge.value + " €")
                self.rows.append(row)
