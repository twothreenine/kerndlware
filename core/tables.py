from django.db import models
from django.db.models import Q
import datetime
from .fields import PercentField
import datetime
import itertools
from .models import *
from .functions import *

class BatchTransactionTable:
    def __init__(self, batch_no):
        self.batch = Batch.objects.get(no=batch_no)
        self.rows = list()
        self.generate()

    def generate(self):
        takings = Taking.objects.filter(batch=self.batch)
        restitutions = Restitution.objects.filter(batch=self.batch)
        specific_purchases = SpecificPurchase.objects.filter(batch=self.batch)
        # cost_sharings = CostSharing.objects.all()
        # proceeds_sharings = ProceedsSharing.objects.all()
        # donations = Donation.objects.all()
        # recoveries = Recovery.objects.all()
        transactions = sorted(list(itertools.chain(takings, restitutions, specific_purchases)), key=lambda t: (t.date, t.id))
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            row = list()
            row.append(transaction.id)
            row.append(transaction.date)
            matter, participants, share = transaction.matter_str(show_contents=False, show_batch=False)
            row.append(matter)
            row.append(transaction.entry_details_str)
            row.append(transaction.value_str())
            row.append(batch_stock_str(transaction))
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
        specific_purchases = SpecificPurchase.objects.filter(batch__consumable=self.consumable_id)
        # cost_sharings = CostSharing.objects.all()
        # proceeds_sharings = ProceedsSharing.objects.all()
        # donations = Donation.objects.all()
        # recoveries = Recovery.objects.all()
        transactions = sorted(list(itertools.chain(takings, restitutions, specific_purchases)), key=lambda t: (t.date, t.id))
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            row = list()
            row.append(transaction.id)
            row.append(transaction.date)
            matter, participants, share = transaction.matter_str()
            row.append(matter)
            row.append(transaction.entry_details_str)
            row.append(transaction.value_str())
            row.append(consumable_stock_str(transaction))
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
        transcriptions_to_balance = TranscriptionToBalance.objects.all()
        payouts = Payout.objects.all()
        transfers = Transfer.objects.all()
        cost_sharings = CostSharing.objects.all()
        proceeds_sharings = ProceedsSharing.objects.all()
        donations = Donation.objects.all()
        recoveries = Recovery.objects.all()
        credits = Credit.objects.all()
        transactions = sorted(list(itertools.chain(takings, restitutions, inpayments, depositations, transcriptions_to_balance, transfers, cost_sharings, proceeds_sharings, donations, recoveries, credits)), key=lambda t: (t.date, t.id))
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
        transcriptions_to_balance = TranscriptionToBalance.objects.filter(originator_account=self.account_id)
        payouts = Payout.objects.filter(originator_account=self.account_id)
        transfers = Transfer.objects.filter(Q(originator_account=self.account_id) | Q(recipient_account=self.account_id))
        cost_sharings = []
        for cs in CostSharing.objects.all():
            if cs.originator_account == acc or cs.participating_accounts.filter(pk=self.account_id).count():
                cost_sharings.append(cs)
        proceeds_sharings = []
        for ps in ProceedsSharing.objects.all():
            if ps.originator_account == acc or ps.participating_accounts.filter(pk=self.account_id).count():
                proceeds_sharings.append(ps)
        donations = []
        for dt in Donation.objects.all():
            if dt.originator_account == acc or dt.participating_accounts.filter(pk=self.account_id).count():
                donations.append(dt)
        recoveries = []
        for rc in Recovery.objects.all():
            if rc.originator_account == acc or rc.participating_accounts.filter(pk=self.account_id).count():
                recoveries.append(rc)
        credits = Credit.objects.filter(originator_account=self.account_id)
        all_transactions = sorted(list(itertools.chain(takings, restitutions, inpayments, depositations, transcriptions_to_balance, payouts, transfers, cost_sharings, proceeds_sharings, donations, recoveries, credits)), key=lambda t: (t.date, t.id))
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
        detailed_types = TransactionType.objects.filter(no__gte=8, no__lte=13)
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            if not transaction.entered_by_user in self.occuring_users:
                self.occuring_users.append(transaction.entered_by_user)
            row = list()
            row.append(transaction.row_color(account=self.account_id)) # 0
            matter, details1, details2 = transaction.matter_str(account=self.account_id)
            if transaction.transaction_type in detailed_types and not details1 == "":
                if details2 == "":
                    show_details = 1
                else:
                    show_details = 2
            else:
                show_details = 0
            row.append(show_details) # 1
            row.append(transaction.id) # 2
            row.append(transaction.date) # 3
            row.append(matter) # 4
            row.append(details1) # 5
            row.append(details2) # 6
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
        if self.transaction.transaction_type.no >= 8 and self.transaction.transaction_type.no <= 11:
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

        if self.transaction.transaction_type.no >= 12 and self.transaction.transaction_type.no <= 13:
            pass

class ProductCategoryTable:
    def __init__(self, objective, account_id=0):
        self.objective = objective
        if account_id == 0:
            self.account_id = Account.objects.all()[0].id
        else:
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
        self.product_stock_details = list()
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
            if self.objective == 'account consumption':
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
            if self.objective == 'consumablelist':
                row.append(p.stock_str) # row 5
                row.append(p.monthly_consumption) # row 6
                row.append(p.taken) # row 7
                row.append(p.on_order) # row 8
                row.append(p.planning) # row 9
                psd = ProductStockDetails(product_id=p.id)
                row.append(psd) # row 10
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

class ProductStockDetails:
    def __init__(self, product_id):
        self.product = Product.objects.get(id=product_id)
        self.emptied_batches = list()
        self.stock_batches = list()
        self.on_order = list()
        self.planned = list()
        self.generate()

    def generate(self):
        batches = Batch.objects.filter(consumable=self.product)
        for b in batches:
            if b.stock == 0 or b.stock <= 0:
                psdbd = ProductStockDetailsBatchDetails(batch_no=b.no)
                self.emptied_batches.append(psdbd)
            elif b.usual_taking_min and b.usual_taking_max:
                pass
            else:
                self.stock_batches.append(b)
        # orders

class ProductStockDetailsBatchDetails:
    def __init__(self, batch_no):
        self.batch = Batch.objects.get(no=batch_no)
        self.rows = list()
        self.generate()

    def generate(self):
        self.rows.append(self.batch.no)
        self.rows.append(self.batch.name)
        self.rows.append(self.batch.supplier)



class SupplierTable:
    def __init__(self):
        self.subtables = list()
        self.generate()

    def generate(self):
        for supplier in Supplier.objects.all():
            sst = SupplierSubtable(supplier=supplier)
            self.subtables.append(sst)

class SupplierSubtable:
    def __init__(self, supplier):
        self.supplier = supplier
        self.broad_location = any_detail_str(object=supplier, attribute='broad_location')
        self.contact_persons = supplier.contact_persons_str()
        self.link_modify = "/admin/core/supplier/"+str(supplier.id)+"/change/?_popup=1"
        self.link_add_go = "/admin/core/generaloffer/add/?distributor="+str(supplier.id)+"&_popup=1"
        self.subsubtables = list()
        self.generate()

    def generate(self):
        for go in GeneralOffer.objects.filter(distributor=self.supplier):
            ssst = SupplierSubsubtable(general_offer=go)
            self.subsubtables.append(ssst)

class SupplierSubsubtable: # ssst
    def __init__(self, general_offer):
        self.general_offer = general_offer
        self.consumable = general_offer.consumable
        self.consumable_variety = general_offer.consumable_variety_str()
        self.original_name = any_detail_str(object=general_offer, attribute='original_name')
        self.supply_stock = general_offer.supply_stock_str()
        self.link_modify = "/admin/core/generaloffer/"+str(general_offer.id)+"/change/?_popup=1"
        self.link_add_o = "/admin/core/offer/add/?general_offer="+str(general_offer.id)+"&_popup=1"
        self.rows = list()
        self.generate()

    def generate(self):
        for o in sorted(Offer.objects.filter(general_offer=self.general_offer), key=lambda t: (t.minimum_amount(), t.id), reverse=True):
            row = list()
            row.append(o.id) # row.0
            row.append(o.amount_str()) # row.1
            row.append(o.total_price_str()) # row.2
            row.append(o.basic_price_str()) # row.3
            row.append("/admin/core/offer/"+str(o.id)+"/change/?_popup=1") # row.4
            row.append(o) # row.5
            row.append(o.minimum_quantity_str())
            self.rows.append(row)

class PurchaseListTable:
    def __init__(self, statuses, start_date, end_date, enterers):
        self.rows = list()
        self.statuses = statuses
        self.start_date = start_date
        self.end_date = end_date
        self.enterers = enterers
        self.generate()

    def generate(self):
        purchases = []
        for p in sorted(Purchase.objects.all(), key=lambda t: t.date, reverse=True):
            if self.statuses == None:
                status_condition = True
            else:
                status_condition = False
                for ss in self.statuses:
                    if ss in p.statuses:
                        status_condition = True
                        break
            if self.start_date == None:
                start_condition = True
            else:
                if p.date >= self.start_date:
                    start_condition = True
                else:
                    start_condition = False
            if self.end_date == None:
                end_condition = True
            else:
                if p.date <= self.end_date:
                    end_condition = True
                else:
                    end_condition = False
            if self.enterers == None:
                enterer_condition = True
            elif p.entered_by_user in self.enterers:
                enterer_condition = True
            else:
                enterer_condition = False
            if status_condition == True and start_condition == True and end_condition == True and enterer_condition == True:
                purchases.append(p)
        for p in purchases:
            row = list()
            row.append(p.id) # row.0
            row.append(p.date) # row.1
            row.append(p.batches_str()) # row.2
            row.append(p.suppliers_str()) # row.3
            row.append(p.status_str()) # row.4
            row.append(p.entered_by_user.name) # row.5
            row.append(p.credited_accounts) # row.6
            self.rows.append(row)