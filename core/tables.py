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
            matter, participants, share = transaction.matter_str(account=0, show_contents=False, show_batch=False)
            row.append(matter)
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
            matter, participants, share = transaction.matter_str(account=0)
            row.append(matter)
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
            matter, participants, share = transaction.matter_str(account=0)
            row.append(matter + participants)
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
        self.occuring_users = []
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
                donations.append(dt)
        # donation = Donation.objects.filter(originator_account=self.account_id) & Donation.objects.filter(participating_accounts=self.account_id)
        recoveries = []
        for rc in Recovery.objects.all():
            if rc.originator_account == acc or rc.participating_accounts.filter(pk=self.account_id).count():
                recoveries.append(rc)
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
        detailed_types = TransactionType.objects.filter(no__gte=8, no__lte=11)
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            if not transaction.entered_by_user in self.occuring_users:
                self.occuring_users.append(transaction.entered_by_user)
            row = list()
            row.append(transaction.row_color(account=self.account_id)) # 0
            if transaction.transaction_type in detailed_types:
                show_details = True
            else:
                show_details = False
            row.append(show_details) # 1
            row.append(transaction.id) # 2
            row.append(transaction.date) # 3
            matter, participants, share = transaction.matter_str(account=self.account_id)
            row.append(matter) # 4
            row.append(participants) # 5
            row.append(share) # 6
            row.append(transaction.transaction_type) # 7
            row.append(transaction.entry_details_str) # 8
            row.append(transaction.value_str(account=self.account_id)) # 9
            row.append(transaction.balance_str(account=self.account_id)) # 10
            row.append(transaction.comment_str) # 11
            if show_details:
                row.append(TrDetailsTable(transaction=transaction)) # 12
            self.rows.append(row)

    # def get(self, row_index, column_index):
    #    return self.rows[row_index][column_index]

    def get_dimensions(self):
        return (len(self.rows), 7) # where is this used ???

class TrDetailsTable:
# Creates a table to show details to a transaction, such as the ID and, in case of cost sharing etc., the individual shares
    def __init__(self, transaction):
        self.transaction = transaction
        self.rows = list()
        self.generate()

    def generate(self):
        shares = list(self.transaction.shares.all())
        if shares:
            if CostSharing.objects.filter(id=self.transaction.id).exists() or ProceedsSharing.objects.filter(id=self.transaction.id).exists() or Donation.objects.filter(id=self.transaction.id).exists() or Recovery.objects.filter(id=self.transaction.id).exists():         
                total_rate = 0
                total_value = 0
                for charge in shares:
                    total_rate += charge.account.calc_rate(datetime=self.transaction.date)
                    total_value += charge.value
                for charge in shares:
                    row = list()
                    row.append(charge.account.name)
                    row.append(str(format(charge.value, '.2f')) + " €")
                    row.append("(" + str(charge.account.calc_rate(datetime=self.transaction.date)) + "x)")
                    if not total_value == 0:
                        row.append(format(charge.value / total_value * 100, '.2f') + "%")
                    self.rows.append(row)
                final_row = list()
                final_row.append("Total (" + str(len(shares)) + " participants)")
                final_row.append(str(format(total_value, '.2f')) + " €")
                final_row.append(str(total_rate) + " shares")
                self.rows.append(final_row)

class ProductCategoryTable:
    def __init__(self, objective, account_id=0):
        self.objective = objective
        self.account_id = account_id
        self.subtables = list()
        self.generate()

    def generate(self):
        prodcats = ProductCategory.objects.all()
        for pc in prodcats:
            if Product.objects.filter(category = pc).count():
                pcs = ProductCategorySubtable(objective=self.objective, account_id=self.account_id, product_category_id=pc.id)
                self.subtables.append(pcs)

                """
                sh_row = list()
                sh_row.append(pc.name)
                sh_row.append(pc.description)
                self.subheadings.append(sh_row)
                sh_p_rows = list()
                for p in prods:
                    p_row = list()
                    p_row.append(p.name)
                    p_row.append(p.description)
                    if p.presumed_price:
                        p_row.append("{} €".format(format(p.presumed_price, '.2f')))
                    else:
                        p_row.append("")
                    p_row.append(p.unit.abbr)
                    # further ones
                    sh_p_rows.append(p_row)
                self.rows.append(sh_p_rows)
                """

class ProductCategorySubtable:
    def __init__(self, objective, account_id, product_category_id):
        self.objective = objective
        self.account_id = account_id
        self.product_category = ProductCategory.objects.get(id=product_category_id)
        self.id = self.product_category.id
        self.heading = self.product_category.name
        self.subheading = self.product_category.description
        self.rows = list()
        self.generate()

    def generate(self):
        prods = Product.objects.filter(category=self.product_category)
        for p in prods:
            row = list()
            row.append(p.id) # row.0
            row.append(p.name) # row.1
            if not p.description == "":
                row.append(p.description) # row.2
            else:
                row.append("") # row.2
            if p.presumed_price:
                row.append("{} €".format(format(p.presumed_price, '.2f'))) # row.3
            else:
                row.append("") # row.3
            row.append(p.unit.abbr) # row.4
            try:
                ce = ConsumptionEstimation.objects.get(account=self.account_id, consumable=p)
                row.append(format(ce.amount, '.3f')) # row.5
                if ce.consumable.presumed_price:
                    pres_value = ce.amount * ce.consumable.presumed_price
                    pv = "{} €".format(format(pres_value, '.2f'))
                else:
                    pv = ''
                row.append(pv) # row.6
            except ConsumptionEstimation.DoesNotExist:
                row.append("") # row.5
                row.append("") # row.6
            # further ones
            self.rows.append(row)

            """
                row = list()
                row.append(pc.name)
                row.append(pc.description)
                self.rows.append(row)
                for prod in prods:
                    row = list()
                    row.append(prod.name)
                    row.append(prod.description)
                    if prod.presumed_price:
                        row.append("{} €".format(format(prod.presumed_price, '.2f')))
                    else:
                        row.append("")
                    row.append(prod.unit.abbr)
                    # further ones
                    self.rows.append(row)
            """