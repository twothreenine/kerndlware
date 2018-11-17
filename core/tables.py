from django.db import models
from django.db.models import Q
import datetime
from .fields import PercentField
import itertools
from .models import *
from .functions import *
from .config import *

class BatchTransactionTable:
    def __init__(self, batch_no, short_date_format):
        self.batch = Batch.objects.get(no=batch_no)
        self.short_date_format = short_date_format
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
            row.append(transaction.date.strftime(self.short_date_format))
            matter, participants, share = transaction.matter_str(show_contents=False, show_batch=False)
            row.append(matter)
            row.append(transaction.entry_details_str(self.short_date_format))
            row.append(transaction.value_str())
            row.append(batch_stock_str(transaction))
            row.append(transaction.comment_str)
            self.rows.append(row)

class ConsumableTransactionTable:
    def __init__(self, consumable_id, short_date_format):
        self.consumable_id = consumable_id
        consumable = Consumable.objects.get(pk=consumable_id)
        batches = Batch.objects.filter(consumable=consumable) # what's done with this??
        self.short_date_format = short_date_format
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
            row.append(transaction.date.strftime(self.short_date_format))
            matter, participants, share = transaction.matter_str()
            row.append(matter)
            row.append(transaction.entry_details_str(self.short_date_format))
            row.append(transaction.value_str())
            row.append(consumable_stock_str(transaction))
            row.append(transaction.comment_str)
            self.rows.append(row)

class TransactionTable:
    def __init__(self, short_date_format):
        self.short_date_format = short_date_format
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
            row.append(transaction.date.strftime(self.short_date_format))
            matter, participants, share = transaction.matter_str(account=0)
            row.append(matter + participants)
            row.append(transaction.entry_details_str(self.short_date_format))
            row.append(transaction.value_str(account=0))
            row.append(transaction.comment_str)
            self.rows.append(row)

class AccountTable:
    def __init__(self, account_id, types, start_date, end_date, short_date_format, enterer):
        self.account_id = account_id
        self.types = types
        self.start_date = start_date
        self.end_date = end_date
        self.short_date_format = short_date_format
        self.enterer = enterer
        self.occuring_profiles = []
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
        all_transactions = sorted(list(itertools.chain(takings, restitutions, inpayments, depositations, transcriptions_to_balance, payouts, transfers, cost_sharings, proceeds_sharings, donations, recoveries, credits)), key=lambda t: (t.date, t.id), reverse=True)
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
            elif self.enterer == tr.entered_by_profile:
                enterer_condition = True
            else:
                enterer_condition = False
            if tr.transaction_type in self.types and start_condition == True and end_condition == True and enterer_condition == True:
                transactions.append(tr)
        detailed_types = TransactionType.objects.filter(no__gte=8, no__lte=13)
        for i in range(0, len(transactions)):
            transaction = transactions[i]
            if not transaction.entered_by_profile in self.occuring_profiles:
                self.occuring_profiles.append(transaction.entered_by_profile)
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
            row.append(transaction.date.strftime(self.short_date_format)) # 3
            row.append(matter) # 4
            row.append(details1) # 5
            row.append(details2) # 6
            row.append(transaction.transaction_type) # 7
            row.append(transaction.entry_details_str(self.short_date_format)) # 8
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
                        total_rate += charge.account.calc_specific_sharings_rate(self.transaction.date)
                        total_value += charge.value
                    for charge in shares:
                        row = list()
                        row.append(charge.account.name)
                        row.append(str(format(charge.value, '.2f')) + " €")
                        row.append("(" + str(charge.account.calc_specific_sharings_rate(self.transaction.date)) + "x)")
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

class MembershipFeePhaseTable:
    def __init__(self, short_date_format, account=None, date=datetime.date.today(), fee=None, hide_inactive=False):
        self.account = account
        self.date = date
        self.short_date_format = short_date_format
        self.fee = fee
        self.hide_inactive = hide_inactive

        self.current_share_sum = ""
        self.current_fee_sum = ""

        self.current_specific_sharings_phases = list()
        self.current_general_phases = list()
        self.current_custom_phases = list()

        self.current_phases = list()
        self.future_phases = list()
        self.former_phases = list()

        # self.future_specific_sharings_phases = list()
        # self.future_general_phases = list()
        # self.future_custom_phases = list()
        # self.former_specific_sharings_phases = list()
        # self.former_general_phases = list()
        # self.former_custom_phases = list()

        self.current_phases_count = 0
        self.future_phases_count = 0
        self.former_phases_count = 0

        self.generate()

    def generate(self):
        # current_share_phases = MembershipFee.objects.filter(account=self.account, mode=MembershipFeeMode.SINGLE_SHARINGS, active=True).filter(Q(start=None)|Q(start__lte=datetime.datetime.now())).filter(Q(end=None)|Q(end__gte=datetime.datetime.now()))
        # if current_share_phases:
        #     rate = 1
        #     for phase in current_share_phases:
        #         rate = rate * phase.rate
        #     self.current_share = rate
        # current_relative_regular_fee_phases = MembershipFee.objects.filter(account=self.account, mode=MembershipFeeMode.REGULAR_RELATIVE, active=True).filter(Q(start=None)|Q(start__lte=datetime.datetime.now())).filter(Q(end=None)|Q(end__gte=datetime.datetime.now()))
        # if current_relative_regular_fee_phases:
        #     relative_daily_rate = 1
        #     default_period = TimePeriod.objects.get(singular="Month") # TODO: select default time period from general settings
        #     for phase in current_relative_regular_fee_phases:
        #         if phase.TimePeriod:
        #             period = phase.TimePeriod
        #         else:
        #             period = default_period
        #         relative_daily_rate += phase.rate * phase.TimePeriod.days
        #     self.current_relative_regular_fee = relative_daily_rate / default_period
        # current_absolute_regular_fee_phases = MembershipFee.objects.filter(account=self.account, mode=MembershipFeeMode.REGULAR_ABSOLUTE, active=True).filter(Q(start=None)|Q(start__lte=datetime.datetime.now())).filter(Q(end=None)|Q(end__gte=datetime.datetime.now()))
        # if current_absolute_regular_fee_phases:
        #     absolute_daily_rate = 0
        #     default_period = TimePeriod.objects.get(singular="Month") # TODO: select default time period from general settings
        #     for phase in current_absolute_regular_fee_phases:
        #         if phase.TimePeriod:
        #             period = phase.TimePeriod
        #         else:
        #             period = default_period
        #         absolute_daily_rate += phase.rate * phase.TimePeriod.days
        #     self.current_absolute_regular_fee = absolute_daily_rate / default_period
        # self.current_total_regular_fee = self.current_relative_regular_fee + self.current_absolute_regular_fee



        self.current_phases = self.list_specific_sharings_phases(time_filter="current") + self.list_general_phases(time_filter="current") + self.list_custom_phases(time_filter="current")
        self.future_phases = self.list_specific_sharings_phases(time_filter="future") + self.list_general_phases(time_filter="future") + self.list_custom_phases(time_filter="future")
        self.former_phases = self.list_specific_sharings_phases(time_filter="former") + self.list_general_phases(time_filter="former") + self.list_custom_phases(time_filter="former")

        self.current_specific_sharings_phases = self.filter_specific_sharings_phases(time_filter="current")
        self.current_general_phases = self.filter_general_phases(time_filter="current")
        self.current_custom_phases = self.filter_custom_phases(time_filter="current")

        if self.current_specific_sharings_phases:
            share_sum = 1
        else:
            share_sum = 0
        for phase in self.current_specific_sharings_phases:
            share_sum = share_sum * phase.rate
        self.current_share_sum = "{}x".format(format(share_sum,'.1f'))

        fee_sum = 0
        per_period = self.account.get_time_period_for_membership_fees()
        if per_period:
            for phase in self.current_general_phases:
                fee_sum += phase.calc_amount(date=self.date, per_period=per_period)
            for phase in self.current_custom_phases:
                fee_sum += phase.rate * per_period.days / (phase.time_period.days*phase.time_period_multiplicator)
            self.current_fee_sum = "{} € per {}".format(format(fee_sum,'.2f'), per_period.singular)
        else:
            self.current_fee_sum = "Error: period not found"

        self.current_phases_count = len(self.current_phases)
        self.future_phases_count = len(self.future_phases)
        self.former_phases_count = len(self.former_phases)

        # future_phases = MembershipFee.objects.filter(account=self.account).filter(Q(start__gt=datetime.datetime.now()))
        # for phase in future_phases:
        #     row = list()
        #     row.append(phase.active)
        #     row.append(phase.start)
        #     row.append(phase.end)
        #     if not phase.mode == MembershipFeeMode.SINGLE_SHARINGS and phase.period:
        #         mode = str(phase.period)+str(phase.mode)
        #     else:
        #         mode = str(phase.mode)
        #     row.append(mode)
        #     row.append(phase.rate)
        #     row.append("by {} on {}".format(phase.last_edited_by, phase.last_edited_on))
        #     self.future_phases.append(row)
        # former_phases = MembershipFee.objects.filter(account=self.account).filter(Q(end__lt=datetime.datetime.now()))
        # for phase in former_phases:
        #     row = list()
        #     row.append(phase.active)
        #     row.append(phase.start)
        #     row.append(phase.end)
        #     if not phase.mode == MembershipFeeMode.SINGLE_SHARINGS and phase.period:
        #         mode = str(phase.period)+str(phase.mode)
        #     else:
        #         mode = str(phase.mode)
        #     row.append(mode)
        #     row.append(phase.rate)
        #     row.append("by {} on {}".format(phase.last_edited_by, phase.last_edited_on))
        #     self.former_phases.append(row)

    def list_specific_sharings_phases(self, time_filter): # filter = 'current' or 'former' or 'future'
        specific_sharings_phases = self.filter_specific_sharings_phases(time_filter=time_filter)
        phases_list = list()
        for phase in specific_sharings_phases:
            row = list()
            row.append(phase.id) # row.0
            row.append(phase.active) # row.1
            if phase.start:
                row.append(phase.start.strftime(self.short_date_format)) # row.2
            else:
                row.append("") # row.2
            if phase.end:
                row.append(phase.end.strftime(self.short_date_format)) # row.3
            else:
                row.append("") # row.3
            row.append("on specific sharings") # row.4 (mode)
            row.append(str(phase.rate)+"x") # row.5
            row.append(phase.comment) # row.6
            row.append("") # row.7 (time period)
            row.append("") # row.8 (next performance)
            row.append("") # row.9 (previous performance)
            row.append("by {} on {}".format(phase.last_edited_by, phase.last_edited_on.strftime(self.short_date_format))) # row.10
            row.append("") # row.11 (no fixed recipient)
            phases_list.append(row)
        return phases_list

    def filter_specific_sharings_phases(self, time_filter): # filter = 'current' or 'former' or 'future'
        if time_filter == "current":
            specific_sharings_phases = [phase for phase in SpecificSharingsMembershipPhase.objects.all() if phase.current(self.date) == True]
            # for phase in SpecificSharingsMembershipPhase.objects.all():
            #     if phase.current(self.date) == True:
            #         specific_sharings_phases.append(phase)
        elif time_filter == "future":
            specific_sharings_phases = SpecificSharingsMembershipPhase.objects.filter(Q(start__gt=datetime.datetime.now()))
        elif time_filter == "former":
            specific_sharings_phases = SpecificSharingsMembershipPhase.objects.filter(Q(end__lt=datetime.datetime.now()))

        if self.account:
            specific_sharings_phases = [phase for phase in specific_sharings_phases if phase.account == self.account]

        return specific_sharings_phases

    def list_general_phases(self, time_filter):
        general_phases = self.filter_general_phases(time_filter=time_filter)
        phases_list = list()
        for phase in general_phases:
            row = list()
            row.append(phase.id) # row.0
            row.append(phase.active) # row.1
            if phase.start:
                row.append(phase.start.strftime(self.short_date_format)) # row.2
            else:
                row.append("") # row.2
            if phase.end:
                row.append(phase.end.strftime(self.short_date_format)) # row.3
            else:
                row.append("") # row.3
            row.append("general fee: "+str(phase.fee.label)) # row.4 (mode)
            row.append(str(phase.rate)+"x ("+format(phase.calc_amount(date=self.date),'.2f')+" €)") # row.5
            row.append(phase.comment) # row.6
            if phase.fee.time_period_multiplicator == 1 and phase.fee.time_period.adjective:
                period_str = phase.fee.time_period.adjective
            else:
                period_str = "every {} {}".format(remove_zeros(phase.fee.time_period_multiplicator), phase.fee.time_period.plural)
            account_main_period = phase.account.get_time_period_for_membership_fees()
            if not account_main_period.days == phase.fee.time_period.days * phase.fee.time_period_multiplicator:
                period_str += " ({} € per {})".format(format(phase.calc_amount(date=self.date, per_period=account_main_period),'.2f'), account_main_period.singular)
            row.append(period_str) # row.7 (time period)
            if phase.fee.next_performance:
                row.append(phase.fee.next_performance.strftime(self.short_date_format)) # row.8 (next performance)
            else:
                row.append("") # row.8 (next performance)
            if phase.fee.previous_performance:
                row.append(phase.fee.previous_performance.strftime(self.short_date_format)) # row.9 (previous performance)
            else:
                row.append("") # row.9 (previous performance)
            row.append("by {} on {}".format(phase.last_edited_by, phase.last_edited_on.strftime(self.short_date_format))) # row.10
            row.append(any_detail_str(object=phase.fee, attribute="recipient_account")) # row.11
            phases_list.append(row)
        return phases_list

    def filter_general_phases(self, time_filter): # filter = 'current' or 'former' or 'future'
        if time_filter == "current":
            general_phases = [phase for phase in GeneralMembershipFeePhase.objects.all() if phase.current(self.date)]
        elif time_filter == "future":
            general_phases = GeneralMembershipFeePhase.objects.filter(Q(start__gt=datetime.datetime.now()))
        elif time_filter == "former":
            general_phases = GeneralMembershipFeePhase.objects.filter(Q(end__lt=datetime.datetime.now()))

        if self.account:
            general_phases = [phase for phase in general_phases if phase.account == self.account]
        if self.fee:
            general_phases = [phase for phase in general_phases if phase.fee == self.fee]
        if self.hide_inactive:
            general_phases = [phase for phase in general_phases if active]

        return general_phases

    def list_custom_phases(self, time_filter):
        custom_phases = self.filter_custom_phases(time_filter=time_filter)
        phases_list = list()
        for phase in custom_phases:
            row = list()
            row.append(phase.id) # row.0
            row.append(phase.active) # row.1
            if phase.start:
                row.append(phase.start.strftime(self.short_date_format)) # row.2
            else:
                row.append("") # row.2
            if phase.end:
                row.append(phase.end.strftime(self.short_date_format)) # row.3
            else:
                row.append("") # row.3
            row.append("custom fee: "+str(phase.label)) # row.4 (mode)
            row.append(format(phase.rate,'.2f')+" €") # row.5
            row.append(phase.comment) # row.6
            if phase.time_period_multiplicator == 1 and phase.time_period.adjective:
                period_str = phase.time_period.adjective
            else:
                period_str = "every {} {}".format(phase.time_period_multiplicator, phase.time_period.plural)
            account_main_period = phase.account.get_time_period_for_membership_fees()
            if not account_main_period.days == phase.time_period.days * phase.time_period_multiplicator:
                period_str += " ({} € per {})".format(format(phase.calc_amount(date=self.date, per_period=account_main_period),'.2f'), account_main_period.singular)
            row.append(period_str) # row.7 (time period)
            if phase.next_performance:
                row.append(phase.next_performance.strftime(self.short_date_format)) # row.8 (next performance)
            else:
                row.append("") # row.8 (next performance)
            if phase.previous_performance:
                row.append(phase.previous_performance.strftime(self.short_date_format)) # row.9 (previous performance)
            else:
                row.append("") # row.9 (previous performance)
            row.append("by {} on {}".format(phase.last_edited_by, phase.last_edited_on.strftime(self.short_date_format))) # row.10
            row.append(any_detail_str(object=phase, attribute="recipient_account")) # row.11
            phases_list.append(row)
        return phases_list

    def filter_custom_phases(self, time_filter): # filter = 'current' or 'former' or 'future'
        if time_filter == "current":
            custom_phases = [phase for phase in CustomMembershipFeePhase.objects.all() if phase.current(self.date)]
        elif time_filter == "future":
            custom_phases = CustomMembershipFeePhase.objects.filter(Q(start__gt=datetime.datetime.now()))
        elif time_filter == "former":
            custom_phases = CustomMembershipFeePhase.objects.filter(Q(end__lt=datetime.datetime.now()))

        if self.account:
            custom_phases = [phase for phase in custom_phases if phase.account == self.account]
        if self.hide_inactive:
            custom_phases = [phase for phase in custom_phases if active]

        return custom_phases

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
    def __init__(self, statuses, start_date, end_date, short_date_format, enterers):
        self.rows = list()
        self.statuses = statuses
        self.start_date = start_date
        self.end_date = end_date
        self.short_date_format = short_date_format
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
            elif p.entered_by_profile in self.enterers:
                enterer_condition = True
            else:
                enterer_condition = False
            if status_condition == True and start_condition == True and end_condition == True and enterer_condition == True:
                purchases.append(p)
        for p in purchases:
            row = list()
            row.append(p.id) # row.0
            row.append(p.date.strftime(self.short_date_format)) # row.1
            row.append(p.batches_str()) # row.2
            row.append(p.suppliers_str()) # row.3
            row.append(p.status_str()) # row.4
            row.append(p.entered_by_profile.name) # row.5
            row.append(p.credited_accounts) # row.6
            self.rows.append(row)

class BalanceSheet:
    def __init__(self, date=datetime.date.today()):
        self.date = date

        self.total_assets = float()
        self.total_current_assets = float()
        self.total_cash = float()
        self.total_inventories = float()
        self.total_prepaid_inventories = float()
        self.total_accounts_receivable = float()
        self.total_prepaid_expenses = float()
        self.total_non_current_assets = float()
        self.total_property_and_equipment = float()
        self.total_other_non_current_assets = float()

        self.cash = list()
        self.inventories = list()
        self.prepaid_inventories = list()
        self.accounts_receivable = list()
        self.prepaid_expences = list()
        self.properties_and_equipment = list()
        self.other_non_current_assets = list()

        # liabilities and stockholders' equity

        self.generate()

    def generate(self):
        pass