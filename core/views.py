from django.db.models import Q
import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import TransactionEntryForm
from .models import *
from .tables import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
import itertools
import logging
from django.db.utils import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from core.config import *

try:

    if not TimePeriod.objects.all():
        day = TimePeriod(singular="day", plural="days", adjective="daily", days=1, decimals_shown=0, is_day=True)
        day.save()
        week = TimePeriod(singular="week", plural="weeks", adjective="weekly", days=7, decimals_shown=1, is_week=True)
        week.save()
        month = TimePeriod(singular="month", plural="months", adjective="monthly", days=30.4375, decimals_shown=1, is_month=True)
        month.save()
        year = TimePeriod(singular="year", plural="years", adjective="annual", days=365.25, decimals_shown=2, is_year=True)
        year.save()

    selected_user = None
    short_date_format = date_format(user=selected_user, style="short")
    long_date_format = date_format(user=selected_user, style="long")
    date_format_codes = ['%Y/%m/%d', '%d.%m.%Y', '%d.%m.%y', '%A, %d. %B %Y', '%A, %B %d, %Y', '%B %d, %Y']
    accounts = Account.objects.all()
    if accounts:
        selected_account = accounts[0]
    else:
        selected_account = Account(name="Test")
        selected_account.save()

    logger = logging.getLogger(__name__)
    batches = Batch.objects.all()
    if batches.count():
        selected_batch_in_batchtransactiontable = batches[0]
    else:
        selected_batch_in_batchtransactiontable = Batch(name="Test", price=0)
        selected_batch_in_batchtransactiontable.save()
    consumables = Consumable.objects.all()
    if consumables.count():
        selected_consumable_in_consumabletransactiontable = consumables[0]
    else:
        selected_consumable_in_consumabletransactiontable = Consumable(name="Test")
        selected_consumable_in_consumabletransactiontable.save()

    # General
    recent_users = list(User.objects.all())
    recent_accounts = Account.objects.all()

    # participate/transactions list filter
    selected_types_in_account_transactions = TransactionType.objects.all()
    start_date_in_account_transactions = models.DateField(blank=True, null=True)
    start_date_in_account_transactions = None # datetime.datetime.strptime('2014-01-01' , '%Y-%m-%d')
    end_date_in_account_transactions = models.DateField(blank=True, null=True)
    end_date_in_account_transactions = None
    enterer_in_account_transactions = models.ForeignKey('User', blank=True, null=True)
    enterer_in_account_transactions = None

    # purchases list filter
    selected_statuses_in_purchase_list = PurchaseStatus.objects.all()
    start_date_in_purchase_list = models.DateField(blank=True, null=True)
    start_date_in_purchase_list = None
    end_date_in_purchase_list = models.DateField(blank=True, null=True)
    end_date_in_purchase_list = None
    enterers_in_purchase_list = list()
    for p in Purchase.objects.all():
        if not p.entered_by_user in enterers_in_purchase_list:
            enterers_in_purchase_list.append(p.entered_by_user)


    # participate/transactions entry form
    default_date_of_new_transaction = models.CharField()
    default_date_of_new_transaction = ""

    if not VirtualUser.objects.filter(name="Bot"):
        bot = VirtualUser(name="Bot", active=False)
        bot.save()

    if not TransactionType.objects.all():
        """
        OLD:
        1 = Taking
        2 = Restitution
        3 = Inpayment
        4 = Depositation
        5 = PayOutBalance
        6 = PayOutDeposit
        7 = Transfer
        8 = CostSharing
        9 = ProceedsSharing
        10 = Donation
        11 = Recovery
        12 = Credit to balance
        13 = Credit to deposit
        
        taking = TransactionType(name="Taking", is_entry_type=True, to_balance=True, no=1)
        taking.save()
        restitution = TransactionType(name="Restitution", is_entry_type=True, to_balance=True, no=2)
        restitution.save()
        inpayment = TransactionType(name="Inpayment", is_entry_type=True, to_balance=True, no=3)
        inpayment.save()
        depositation = TransactionType(name="Depositation", is_entry_type=True, to_balance=False, no=4)
        depositation.save()
        pay_out_balance = TransactionType(name="Balance payout", is_entry_type=False, to_balance=True, no=5)
        pay_out_balance.save()
        pay_out_deposit = TransactionType(name="Deposit payout", is_entry_type=False, to_balance=False, no=6)
        pay_out_deposit.save()
        transfer = TransactionType(name="Transfer", is_entry_type=True, to_balance=True, no=7)
        transfer.save()
        cost_sharing = TransactionType(name="Cost sharing", is_entry_type=True, to_balance=True, no=8)
        cost_sharing.save()
        proceeds_sharing = TransactionType(name="Proceeds sharing", is_entry_type=True, to_balance=True, no=9)
        proceeds_sharing.save()
        donation = TransactionType(name="Donation", is_entry_type=True, to_balance=True, no=10)
        donation.save()
        recovery = TransactionType(name="Recovery", is_entry_type=True, to_balance=True, no=11)
        recovery.save()
        credit_to_balance = TransactionType(name="Credit to balance", is_entry_type=False, to_balance=True, no=12)
        credit_to_balance.save()
        credit_to_deposit = TransactionType(name="Credit to deposit", is_entry_type=False, to_balance=False, no=13)
        credit_to_deposit.save()

        NEW:

        1 = Taking (charged from balance or deposit)
        2 = Restitution (credited to balance or deposit)
        3 = Inpayment (credited to balance)
        4 = Depositation (credited to deposit, charged from balance)
        5 = Transcription to balance (credited to balance, charged from deposit)
        6 = Payout (charged from balance)
        7 = Transfer (charged from one's balance, credited to another's balance)
        8 = CostSharing         # 8 = Division (positive value: charged from one's balance, credited to various' balances; negative value: credited to one's balance, charged from various' balances)
        9 = ProceedsSharing
        10 = Donation
        11 = Recovery
        12 = Credit (credited to balance)
        """

        taking = TransactionType(name="Taking", is_entry_type=True, no=1)
        taking.save()
        restitution = TransactionType(name="Restitution", is_entry_type=True, no=2)
        restitution.save()
        inpayment = TransactionType(name="Inpayment", is_entry_type=True, no=3)
        inpayment.save()
        payout = TransactionType(name="Payout", is_entry_type=False, no=4)
        payout.save()
        depositation = TransactionType(name="Depositation", is_entry_type=True, no=5)
        depositation.save()
        transcription_to_balance = TransactionType(name="Transcription to balance", is_entry_type=False, no=6)
        transcription_to_balance.save()
        transfer = TransactionType(name="Transfer", is_entry_type=True, no=7)
        transfer.save()
        cost_sharing = TransactionType(name="Cost sharing", is_entry_type=True, no=8)
        cost_sharing.save()
        proceeds_sharing = TransactionType(name="Proceeds sharing", is_entry_type=True, no=9)
        proceeds_sharing.save()
        donation = TransactionType(name="Donation", is_entry_type=True, no=10)
        donation.save()
        recovery = TransactionType(name="Recovery", is_entry_type=True, no=11)
        recovery.save()
        credit = TransactionType(name="Credit", is_entry_type=False, no=12)
        credit.save()

    if not PurchaseStatusType.objects.all(): # fix types of purchase statuses
        nonbinding = PurchaseStatusType(name="nonbinding", no=1)
        nonbinding.save()
        binding = PurchaseStatusType(name="binding", no=2)
        binding.save()
        closed = PurchaseStatusType(name="closed", no=3)
        closed.save()
        waste = PurchaseStatusType(name="waste", no=4)
        waste.save()

    if not PurchaseStatus.objects.all(): # default statuses which can be renamed, deleted, and added
        planned = PurchaseStatus(name="planned", purchase_status_type=PurchaseStatusType.objects.get(no=1))
        planned.save()
        to_be_ordered = PurchaseStatus(name="to be ordered", purchase_status_type=PurchaseStatusType.objects.get(no=2))
        to_be_ordered.save()
        ordered = PurchaseStatus(name="ordered", purchase_status_type=PurchaseStatusType.objects.get(no=2))
        ordered.save()
        delivered = PurchaseStatus(name="delivered", purchase_status_type=PurchaseStatusType.objects.get(no=2))
        delivered.save()
        not_delivered = PurchaseStatus(name="not delivered", purchase_status_type=PurchaseStatusType.objects.get(no=2))
        not_delivered.save()
        questionable = PurchaseStatus(name="questionable", purchase_status_type=PurchaseStatusType.objects.get(no=2))
        questionable.save()
        inserted = PurchaseStatus(name="inserted", purchase_status_type=PurchaseStatusType.objects.get(no=3)) # populated into database
        inserted.save()
        picked_up = PurchaseStatus(name="picked up", purchase_status_type=PurchaseStatusType.objects.get(no=3))
        picked_up.save()
        scrapped = PurchaseStatus(name="scrapped", purchase_status_type=PurchaseStatusType.objects.get(no=4))
        scrapped.save()
        aborted = PurchaseStatus(name="aborted", purchase_status_type=PurchaseStatusType.objects.get(no=4))
        aborted.save()

except OperationalError:
    pass

# perform fees

# now = datetime.datetime.now()
# update_fees(to_datetime=now)

# def update_fees(to_datetime=datetime.datetime.now()):
#     updated_general_fees_count = 0
#     updated_custom_fees_count = 0
#     for fee in GeneralMembershipFee.objects.exclude(next_performance=None, enabled=False, amount__lte=0).filter(next_performance__lte=now): # .filter(Q(start=None)|Q(start__lte=now)).filter(Q(end=None)|Q(end__gte=now)):
#         fee.update(to_datetime=now)
#         updated_general_fees_count += 1
#     for fee in CustomMembershipFeePhase.objects.exclude(next_performance=None, enabled=False, rate__lte=0).filter(next_performance__lte=now):
#         fee.update(to_datetime=now)
#         updated_custom_fees_count += 1
#     print("Fee update schedule: {} general fees updated, {} custom fees updated.".format(updated_general_fees_count, updated_custom_fees_count))

# TODO: Timer/schedule


def select_user(request):
    if request.method == 'POST':
        user_id = request.POST.get("user_id")
        if user_id:
            global selected_user
            global short_date_format
            global long_date_format
            if int(user_id) == 0:
                selected_user = None
                short_date_format = date_format(user=None, style="short")
                long_date_format = date_format(user=None, style="long")
            else:
                selected_user = User.objects.get(pk=int(user_id))
                short_date_format = date_format(user=selected_user, style="short")
                long_date_format = date_format(user=selected_user, style="long")
                global recent_users
                i = recent_users.index(selected_user)
                recent_users.insert(0, recent_users.pop(i))

def create_user(request):
    if request.method == 'POST':
        name = str(request.POST.get("name"))
        notice = str(request.POST.get("notice"))
        if request.POST.get("is_non_real"):
            u = VirtualUser(name=name, notice=notice)
            u.save()
        else:
            u = Person(name=name, notice=notice)
            u.first_name = str(request.POST.get("first_name"))
            u.last_name = str(request.POST.get("last_name"))
            u.streetname = str(request.POST.get("streetname"))
            u.streetnumber = str(request.POST.get("streetnumber"))
            u.zipcode = str(request.POST.get("zipcode"))
            u.town = str(request.POST.get("town"))
            u.country = str(request.POST.get("country"))
            u.address_notice = str(request.POST.get("address_notice"))
            u.email = str(request.POST.get("email"))
            u.website = str(request.POST.get("website"))
            u.telephone1 = str(request.POST.get("telephone1"))
            u.telephone2 = str(request.POST.get("telephone2"))
            u.save()
        if request.POST.getlist("accounts"):
            for acc in request.POST.getlist("accounts"):
                acc = Account.objects.get(pk=int(acc))
                acc.users.add(u)
                acc.save()
                u.accounts.add(acc)
                u.save()
        if not request.POST.get("new_account") == '':
            a = Account(name=str(request.POST.get("new_account")))
            a.save()
            u.accounts.add(a)
            u.save()
            a.users.add(u)
        global selected_user
        selected_user = u

def modify_user(request, selected_user_is_person):
    if request.method == 'POST':
        global selected_user
        selected_user.name = str(request.POST.get("name"))
        selected_user.notice = str(request.POST.get("notice"))
        if selected_user_is_person:
            selected_user.person.first_name = str(request.POST.get("first_name"))
            selected_user.person.last_name = str(request.POST.get("last_name"))
            selected_user.person.streetname = str(request.POST.get("streetname"))
            selected_user.person.streetnumber = str(request.POST.get("streetnumber"))
            selected_user.person.zipcode = str(request.POST.get("zipcode"))
            selected_user.person.town = str(request.POST.get("town"))
            selected_user.person.country = str(request.POST.get("country"))
            selected_user.person.address_notice = str(request.POST.get("address_notice"))
            selected_user.person.email = str(request.POST.get("email"))
            selected_user.person.website = str(request.POST.get("website"))
            selected_user.person.telephone1 = str(request.POST.get("telephone1"))
            selected_user.person.telephone2 = str(request.POST.get("telephone2"))
            selected_user.person.save()
        new_accountlist = list()
        for acc in request.POST.getlist("accounts"):
            acc = Account.objects.get(pk=int(acc))
            new_accountlist.append(acc)
        old_accountlist = selected_user.accounts.all()
        accounts_to_add = [acc for acc in new_accountlist if acc not in old_accountlist]
        accounts_to_remove = [acc for acc in old_accountlist if acc not in new_accountlist]
        for acc in accounts_to_add:
            acc.users.add(selected_user)
            acc.save()
            selected_user.accounts.add(acc)
        for acc in accounts_to_remove:
            acc.users.remove(selected_user)
            acc.save()
            selected_user.accounts.remove(acc)
        pacc = request.POST.get("primary_account")
        if pacc:
            if int(pacc) == 0:
                selected_user.primary_account = None
            else:
                selected_user.primary_account = Account.objects.get(pk=int(pacc))
        if str(request.POST.get("active")) == "yes":
            selected_user.active = True
        else:
            selected_user.active = False
        
        if request.POST.get("short_date_format") == 'custom':
            if request.POST.get("custom_short_date_format"):
                selected_user.short_date_format = request.POST.get("custom_short_date_format")
        elif request.POST.get("short_date_format") == 'default':
            selected_user.short_date_format = ''
        else:
            selected_user.short_date_format = request.POST.get("short_date_format")

        if request.POST.get("long_date_format") == 'custom':
            if request.POST.get("custom_long_date_format"):
                selected_user.long_date_format =  request.POST.get("custom_long_date_format")
        elif request.POST.get("long_date_format") == 'default':
            selected_user.long_date_format = ''
        else:
            selected_user.long_date_format = request.POST.get("long_date_format")
        selected_user.save()

def select_account(request):
    if request.method == 'POST':
        account_id = request.POST.get("account_id")
        primary = request.POST.get("primary_account")
        global selected_account
        if primary:
            global selected_user
            if selected_user:
                if selected_user.primary_account:
                    selected_account = selected_user.primary_account
                elif selected_user.accounts.all():
                    selected_account = selected_user.accounts.all()[0]
                else:
                    print("Error: User {} has no associated accounts.".format(str(selected_user)))
        elif account_id:
            account_id = int(account_id)
            selected_account = Account.objects.get(pk=account_id)

def select_batch_for_batchtransactiontable(request):
    if request.method == 'POST':
        batch_no = request.POST.get("batch_no")
        if batch_no:
            batch_no = int(batch_no)
            global selected_batch_in_batchtransactiontable
            selected_batch_in_batchtransactiontable = Batch.objects.get(no=batch_no)

def select_consumable_for_consumabletransactiontable(request):
    if request.method == 'POST':
        consumable_id = request.POST.get("consumable_id")
        if consumable_id:
            consumable_id = int(consumable_id)
            global selected_consumable_in_consumabletransactiontable
            selected_consumable_in_consumabletransactiontable = Consumable.objects.get(pk=consumable_id)

def filter_account_transactions(request):
    global short_date_format
    if request.method == 'POST':
        transaction_types = request.POST.getlist("transaction_type")
        global selected_types_in_account_transactions
        selected_types_in_account_transactions = []
        if transaction_types:
            for t in transaction_types:
                t = int(t)
                tt = TransactionType.objects.get(no=t)
                selected_types_in_account_transactions.append(tt)
        start_date = request.POST.get("start_date")
        global start_date_in_account_transactions
        if start_date:
            start_date_in_account_transactions = datetime.datetime.strptime(start_date, short_date_format).date()
        else:
            start_date_in_account_transactions = None
        end_date = request.POST.get("end_date")
        global end_date_in_account_transactions
        if end_date:
            end_date_in_account_transactions = datetime.datetime.strptime(end_date, short_date_format).date()
        else:
            end_date_in_account_transactions = None
        enterer = request.POST.get("enterer")
        global enterer_in_account_transactions
        if enterer:
            enterer_id = int(enterer)
            if enterer_id == 0:
                enterer_in_account_transactions = None
            else:
                enterer_in_account_transactions = User.objects.get(pk=enterer_id)
        else:
            enterer_in_account_transactions = None

def enter_new_transaction(request):
    global short_date_format
    if request.method == 'POST':
        transaction_type = request.POST.get("type")
        if transaction_type:
            t_type = TransactionType.objects.get(no=int(transaction_type))
        else:
            t_type = None
        # entered_by = request.POST.get("entered_by")
        # if entered_by:
        #     t_enterer = User.objects.get(pk=int(entered_by))
        #     global default_enterer_of_new_transaction
        #     default_enterer_of_new_transaction = t_enterer
        #     global recent_users
        #     i = recent_users.index(t_enterer)
        #     recent_users.insert(0, recent_users.pop(i))
        date = request.POST.get("date")
        if date:
            t_date = datetime.datetime.strptime(date, short_date_format).date()
            global default_date_of_new_transaction
            default_date_of_new_transaction = date
        amount = request.POST.get("amount")
        if amount:
            t_amount = float(amount)
        comment = request.POST.get("comment")
        if comment:
            t_comment = str(comment)
        else:
            t_comment = ''
        if not t_type == None:
            global selected_account
            if t_type.no == 1: # taking
                batch_no = request.POST.get("batch_no")
                if batch_no:
                    t_batch = Batch.objects.get(no=int(batch_no))
                if t_date and t_amount and t_batch:
                    t = Taking(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment, batch=t_batch)
                    t.save()
                    t.perform()
            elif t_type.no == 2: # restitution
                batch_no = request.POST.get("batch_no")
                if batch_no:
                    t_batch = Batch.objects.get(no=int(batch_no))
                if t_date and t_amount and t_batch:
                    t = Restitution(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment, batch=t_batch)
                    t.save()
                    t.perform()
            elif t_type.no == 3: # inpayment
                currency = request.POST.get("currency")
                if currency:
                    t_currency = Currency.objects.get(pk=int(currency))
                else:
                    t_currency = Currency.objects.get(pk=1) # get anchor currency
                money_box = request.POST.get("money_box")
                if money_box:
                    t_money_box = MoneyBox.objects.get(pk=int(money_box))
                if t_date and t_amount and t_currency and t_money_box:
                    t = Inpayment(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment, currency=t_currency, money_box=t_money_box)
                    t.save()
                    t.perform()
            elif t_type.no == 4: # depositation
                if t_date and t_amount:
                    t = Depositation(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment)
                    t.save()
                    t.perform()
            # elif t_type.no == 5: # transcription of balance (currently not an entry type)
            #     if t_date and t_amount:
            #         t = Transcription_to_balance(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment)
            #         t.save()
            #         t.perform()
            elif t_type.no == 7: # transfer
                recipient_account = request.POST.get("recipient_account")
                if recipient_account:
                    t_recipient_account = Account.objects.get(pk=int(recipient_account))
                if t_date and t_amount and t_recipient_account:
                    t = Transfer(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment, recipient_account=t_recipient_account)
                    t.save()
                    t.perform()
            elif t_type.no == 8 or t_type.no == 9 or t_type.no == 10 or t_type.no == 11: # cost sharing, proceeds sharing, donation, recovery
                participating_accounts = request.POST.getlist("participating_accounts")
                t_participating_accounts = []
                if participating_accounts:
                    for p in participating_accounts:
                        pa = Account.objects.get(pk=int(p))
                        t_participating_accounts.append(pa)
                if t_date and t_amount and t_participating_accounts:
                    if t_type.no == 8:
                        t = CostSharing(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment)
                    if t_type.no == 9:
                        t = ProceedsSharing(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment)
                    if t_type.no == 10:
                        t = Donation(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment)
                    if t_type.no == 11:
                        t = Recovery(originator_account=selected_account, date=t_date, entered_by_user=selected_user, amount=t_amount, comment=t_comment)
                    t.save()
                    t.perform(transaction_type_no=t_type.no, participating_accounts=t_participating_accounts)

def create_account(request):
    if request.method == 'POST':
        a = Account(name=str(request.POST.get("name")))
        a.save()
        if request.POST.getlist("users"):
            for us in request.POST.getlist("users"):
                us = User.objects.get(pk=int(us))
                us.save()
                us.accounts.add(a)
                us.save()
                a.users.add(us)
                a.save()
        if not request.POST.get("new_user") == '':
            if request.POST.get("is_non_real") == True:
                u = User(name=str(request.POST.get("new_user")))
            else:
                u = Person(name=str(request.POST.get("new_user")), last_name='', first_name='')
            u.save()
            u.accounts.add(a)
            u.save()
            a.users.add(u)
            a.save()

def modify_account(request):
    if request.method == 'POST':
        global selected_account
        selected_account.name = str(request.POST.get("name"))
        # selected_user.accounts.clear()
        # for acc in request.POST.getlist("accounts"):
        #     acc = Account.objects.get(pk=int(acc))
        #     acc.users.add(selected_user)
        #     acc.save()
        #     selected_user.accounts.add(acc)
        new_userlist = list()
        for us in request.POST.getlist("users"):
            us = User.objects.get(pk=int(us))
            new_userlist.append(us)
        old_userlist = selected_account.users.all()
        users_to_add = [user for user in new_userlist if user not in old_userlist]
        users_to_remove = [user for user in old_userlist if user not in new_userlist]
        for user in users_to_add:
            user.accounts.add(selected_account)
            user.save()
            selected_account.users.add(user)
        for user in users_to_remove:
            user.accounts.remove(selected_account)
            user.save()
            selected_account.users.remove(user)
        if not request.POST.get("new_user") == '':
            if request.POST.get("is_non_real"):
                u = VirtualUser(name=str(request.POST.get("new_user")))
            else:
                u = Person(name=str(request.POST.get("new_user")))
            u.save()
            u.accounts.add(selected_account)
            u.save()
            selected_account.users.add(u)
        if str(request.POST.get("active")) == "yes":
            selected_account.active = True
        else:
            selected_account.active = False
        displayed_time_period_for_membership_fees = int(request.POST.get("displayed_time_period_for_membership_fees"))
        if displayed_time_period_for_membership_fees == 0:
            selected_account.displayed_time_period_for_membership_fees = None
        else:
            selected_account.displayed_time_period_for_membership_fees = TimePeriod.objects.get(id=displayed_time_period_for_membership_fees)
        selected_account.save()

def modify_consumablelist(request):
    if request.method == 'POST':
        for consumable in Consumable.objects.all():
            if request.POST.get("{}_active".format(consumable.id)):
                consumable.active = True
            else:
                consumable.active = False            
            consumable.name = str(request.POST.get("{}_name".format(consumable.id)))
            consumable.unit = Unit.objects.get(pk=int(request.POST.get("{}_unit".format(consumable.id))))
            consumable.save()

def filter_purchases(request):
    global short_date_format
    if request.method == 'POST':
        purchase_statuses = request.POST.getlist("purchase_statuses")
        global selected_statuses_in_purchase_list
        selected_statuses_in_purchase_list = []
        if purchase_statuses:
            for p in purchase_statuses:
                ps = PurchaseStatus.objects.get(id=int(p))
                selected_statuses_in_purchase_list.append(ps)
        start_date = request.POST.get("start_date")
        global start_date_in_purchase_list
        if start_date:
            start_date_in_purchase_list = datetime.datetime.strptime(start_date , short_date_format).date()
        else:
            start_date_in_purchase_list = None
        end_date = request.POST.get("end_date")
        global end_date_in_purchase_list
        if end_date:
            end_date_in_purchase_list = datetime.datetime.strptime(end_date , short_date_format).date()
        else:
            end_date_in_purchase_list = None
        enterers = request.POST.getlist("enterers")
        global enterers_in_purchase_list
        enterers_in_purchase_list = []
        if enterers:
            for er in enterers:
                e = User.objects.get(id=int(er))
                enterers_in_purchase_list.append(e)

def modify_general_settings(request):
    if request.method == 'POST':
        set_config("group_title", request.POST.get("group_title"))
        # set_config(main_language, request.POST.get("main_language"))

        set_config("anchor_currency", request.POST.get("anchor_currency"))
        
        if request.POST.get("short_date_format") == 'custom':
            if request.POST.get("custom_short_date_format"):
                set_config("short_date_format", request.POST.get("custom_short_date_format"))
        else:
            set_config ("short_date_format", request.POST.get("short_date_format"))

        if request.POST.get("long_date_format") == 'custom':
            if request.POST.get("custom_long_date_format"):
                set_config("long_date_format", request.POST.get("custom_long_date_format"))
        else:
            set_config ("long_date_format", request.POST.get("long_date_format"))

        if request.POST.get("single_sharings"):
            set_boolean_config("single_sharings", True)
        else:
            set_boolean_config("single_sharings", False)

        if request.POST.get("regular_relative_sharings"):
            set_boolean_config("regular_relative_sharings", True)
        else:
            set_boolean_config("regular_relative_sharings", False)

        if request.POST.get("regular_absolute_sharings"):
            set_boolean_config("regular_absolute_sharings", True)
        else:
            set_boolean_config("regular_absolute_sharings", False)
        # set_config(regular_relative_sharings, request.POST.get("regular_relative_sharings"))
        # set_config(regular_absolute_sharings, request.POST.get("regular_absolute_sharings"))
        set_config("displayed_time_period_for_membership_fees", request.POST.get("displayed_time_period_for_membership_fees"))




def global_context(request):
    global recent_users
    global recent_accounts
    global selected_user
    global selected_account
    global short_date_format
    accounts_of_selected_user = []
    recent_other_accounts = []
    if selected_user:
        for account in recent_accounts:
            if selected_user:
                if account.users.filter(id=selected_user.id).count(): # if selected_user is a user related to account
                    accounts_of_selected_user.append(account)
                else:
                    recent_other_accounts.append(account)
    else:
        selected_account = recent_accounts[0]
        # recent_other_accounts = recent_accounts
    accounts = Account.objects.all()
    balance = selected_account.balance_str
    current_path = request.get_full_path()
    context = { "recent_users" : recent_users, "selected_user" : selected_user, "accounts_of_selected_user": accounts_of_selected_user, 
                "recent_other_accounts" : recent_other_accounts, "balance" : balance, "selected_account" : selected_account, "current_path" : current_path, 
                "bootstrap_date_format" : bootstrap_date_format(short_date_format), 
                }
    return context

def base(request):
    if request.method == 'POST':
        if request.POST["form_name"] == "user_selection_form":
            select_user(request)
        if request.POST["form_name"] == "account_selection_form":
            select_account(request)
    return HttpResponseRedirect(request.POST['current_path'])

def index(request):
    template = loader.get_template('core/index.html')
    
    context = { }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def register_user(request):
    create_user(request)
    template = loader.get_template('core/register_user.html')
    accounts = Account.objects.all()
    context = {"accounts" : accounts}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def user_settings(request):
    global selected_user
    selected_user_is_person = False
    short_date_format = None
    long_date_format = None
    short_date_format_example = None
    long_date_format_example = None
    if selected_user:
        try:
            sup = selected_user.person
            selected_user_is_person = True
        except ObjectDoesNotExist:
            pass
        except:
            raise
        short_date_format = selected_user.short_date_format
        long_date_format = selected_user.long_date_format
        if short_date_format:
            short_date_format_example = datetime.date.today().strftime(short_date_format)
        if long_date_format:
            long_date_format_example = datetime.date.today().strftime(long_date_format)
    modify_user(request, selected_user_is_person)
    template = loader.get_template('core/user_settings.html')
    accounts = Account.objects.all()

    global date_format_codes
    date_formats = dict()
    for code in date_format_codes:
        date_formats[code] = datetime.date.today().strftime(code)

    context = { "selected_user" : selected_user, "accounts" : accounts, "selected_user_is_person" : selected_user_is_person, 
                "date_formats" : date_formats, "short_date_format" : short_date_format, "long_date_format" : long_date_format,
                "short_date_format_example" : short_date_format_example, "long_date_format_example" : long_date_format_example,
                "default_short_date_format" : get_config("short_date_format"), "default_long_date_format" : get_config("long_date_format"),
                "default_short_date_format_example" : datetime.date.today().strftime(get_config("short_date_format")), "default_long_date_format_example" : datetime.date.today().strftime(get_config("long_date_format")), 
                }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def account_transactions(request):
    global short_date_format
    if request.method == 'POST':
        if request.POST["form_name"] == "transaction_list_filter":
            filter_account_transactions(request) 
        if request.POST["form_name"] == "transaction_entry_form":
            enter_new_transaction(request)
    template = loader.get_template('core/account_transactions.html')
    global selected_account
    deposit = selected_account.deposit_str
    taken = selected_account.taken_str
    transaction_types = TransactionType.objects.all()
    global selected_types_in_account_transactions
    selected_type_nos = []
    for ttype in selected_types_in_account_transactions:
        selected_type_nos.append(ttype.no)
    global start_date_in_account_transactions
    if not start_date_in_account_transactions == None:
        start_date = start_date_in_account_transactions.strftime(date_format(user=selected_user))
    else:
        start_date = ''
    global end_date_in_account_transactions
    if not end_date_in_account_transactions == None:
        end_date = end_date_in_account_transactions.strftime(date_format(user=selected_user))
    else:
        end_date = ''
    global enterer_in_account_transactions
    transactions = Transaction.objects.all()
    account_table = AccountTable(account_id = selected_account.id, types = selected_types_in_account_transactions, start_date = start_date_in_account_transactions, end_date = end_date_in_account_transactions, 
                                 short_date_format = short_date_format, enterer = enterer_in_account_transactions)
    if request.method == 'POST':
        entry_form = TransactionEntryForm(request.POST)
        if entry_form.is_valid():
            print(entry_form)
            pass
            #return HttpResponseRedirect('/')
    else:
        entry_form = TransactionEntryForm()
    entry_types = TransactionType.objects.filter(is_entry_type=True)

    # users_of_selected_account = selected_account.users.all # list(selected_account.users.all()) ??
    # global recent_users
    # users_of_selected_account = []
    # recent_other_users = []
    # for user in recent_users:
    #     if user.accounts.filter(id=selected_account.id).count(): # if selected_account is an account related to user
    #         users_of_selected_account.append(user)
    #     else:
    #         recent_other_users.append(user)

    table_users_of_selected_account = []
    other_table_users = []
    for user in account_table.occuring_users:
        if user.accounts.filter(id=selected_account.id).count(): # if selected_account is an account related to user
            table_users_of_selected_account.append(user)
        else:
            other_table_users.append(user)
    """
    for user in list(selected_account.users.all()):
        users_of_selected_account.append(user)
        i = recent_other_users.index(user)
        # recent_other_users.pop(i)
        print(recent_users)
    """

    batches = Batch.objects.all()
    currencies = Currency.objects.all()
    money_boxes = MoneyBox.objects.all()
    accounts = Account.objects.all()
    accounts_except_itself = Account.objects.exclude(id=selected_account.id)
    global default_date_of_new_transaction

    context = {
        "account_table" : account_table, "deposit" : deposit,
        "taken" : taken, "entry_form" : entry_form, "entry_types" : entry_types,
        "currencies" : currencies, "money_boxes" : money_boxes,
        "batches" : batches, "transaction_types" : transaction_types, "selected_type_nos" : selected_type_nos, 
        "start_date" : start_date, "end_date" : end_date, "enterer_in_account_transactions" : enterer_in_account_transactions,
        "accounts_except_itself" : accounts_except_itself, "accounts" : accounts,
        "table_users_of_selected_account" : table_users_of_selected_account, "other_table_users" : other_table_users, 
        "default_date_of_new_transaction" : default_date_of_new_transaction,
    }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def register_account(request):
    create_account(request)
    template = loader.get_template('core/register_account.html')
    users = User.objects.all()
    context = {"users" : users}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def account_consumption_form(request):
    if request.method == 'POST':
        global selected_account
        for p in Product.objects.all():
            estimation = request.POST.get(str(p.id))
            if not estimation == "" and not estimation == None:
                estimation = float(estimation)
                try:
                    ce = ConsumptionEstimation.objects.get(account=selected_account, consumable=p)
                    ce.amount = estimation
                    ce.save()
                except ConsumptionEstimation.DoesNotExist:
                    ce = ConsumptionEstimation(account=selected_account, consumable=p, amount=estimation)
                    ce.save()


def account_consumption(request):
    account_consumption_form(request)
    template = loader.get_template('core/account_consumption.html')
    global selected_account
    product_category_table = ProductCategoryTable(objective="account consumption", account_id=selected_account)
    product_category_subtables = product_category_table.subtables
    consumables = Consumable.objects.all()
    total_amount = 0
    total_pres_value = 0
    for ce in ConsumptionEstimation.objects.filter(account=selected_account):
        total_amount += ce.amount * ce.consumable.unit.weight / 1000
        if ce.consumable.presumed_price:
            total_pres_value += ce.amount * ce.consumable.presumed_price
    context = {"account" : selected_account, "consumables" : consumables, "product_category_table" : product_category_table, "product_category_subtables" : product_category_subtables, 
                "total_amount" : "{} kg".format(format(total_amount, '.3f')), "total_pres_value" : "{} €".format(format(total_pres_value, '.2f')), }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def account_membership_fees(request):
    template = loader.get_template('core/account_membership_fees.html')
    global selected_account
    table = MembershipFeePhaseTable(short_date_format, account=selected_account)
    context = {"account" : selected_account, "table" : table}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def account_settings(request):
    modify_account(request)
    template = loader.get_template('core/account_settings.html')
    global selected_account
    users = User.objects.all()
    all_time_periods = TimePeriod.objects.all()
    general_displayed_time_period_for_membership_fees = get_config("displayed_time_period_for_membership_fees")
    context = {"account" : selected_account, "users" : users, "all_time_periods" : all_time_periods, 
                "general_displayed_time_period_for_membership_fees" : general_displayed_time_period_for_membership_fees, }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def suppliers(request):
    # modify_supplier(request) # TODO
    template = loader.get_template('core/suppliers.html')
    supplier_table = SupplierTable()
    context = {"supplier_table" : supplier_table }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def transactionlist(request):
    template = loader.get_template('core/transactionlist.html')
    transaction_table = TransactionTable(short_date_format)
    context = {"transaction_table" : transaction_table}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def batchtransactiontable(request):
    select_batch_for_batchtransactiontable(request)
    global selected_batch_in_batchtransactiontable
    batch_transaction_table = BatchTransactionTable(selected_batch_in_batchtransactiontable.no, short_date_format)
    batches = Batch.objects.all()
    stock = selected_batch_in_batchtransactiontable.stock_str_long(show_contents=False)
    price = selected_batch_in_batchtransactiontable.price_str_long()
    unit_weight = selected_batch_in_batchtransactiontable.unit_weight_str()
    template = loader.get_template('core/batchtransactiontable.html')
    context = {"batches" : batches, "stock" : stock, "batch_transaction_table" : batch_transaction_table, "selected_batch_in_batchtransactiontable" : selected_batch_in_batchtransactiontable, "unit_weight" : unit_weight, "price" : price, }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def consumabletransactiontable(request):
    select_consumable_for_consumabletransactiontable(request)
    global selected_consumable_in_consumabletransactiontable
    consumable_transaction_table = ConsumableTransactionTable(selected_consumable_in_consumabletransactiontable.id, short_date_format)
    consumables = Consumable.objects.all()
    stock = selected_consumable_in_consumabletransactiontable.stock_str_long(show_contents=False)
    unit_weight = selected_consumable_in_consumabletransactiontable.unit_weight_str()
    template = loader.get_template('core/consumabletransactiontable.html')
    context = {"consumables" : consumables, "stock" : stock, "consumable_transaction_table" : consumable_transaction_table, "selected_consumable_in_consumabletransactiontable" : selected_consumable_in_consumabletransactiontable, "unit_weight" : unit_weight, }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def accountlist(request):
    template = loader.get_template('core/accountlist.html')
    accounts = Account.objects.all()
    accountlist = sorted(list(accounts), key=lambda t: t.id)
    context = {"accountlist" : accountlist}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def batchlist(request):
    template = loader.get_template('core/batchlist.html')
    batches = Batch.objects.all()
    batchlist = sorted(list(batches), key=lambda t: t.no)
    context = {"batchlist" : batchlist}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def batchlist_modify(request):
    template = loader.get_template('core/batchlist_modify.html')
    batches = Batch.objects.all()
    batchlist = sorted(list(batches), key=lambda t: t.no)
    context = {"batchlist" : batchlist}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def itemlist(request):
    template = loader.get_template('core/itemlist.html')
    items = Item.objects.all()
    itemlist = sorted(list(items), key=lambda t: t.id)
    context = {"itemlist" : itemlist}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def consumablelist(request):
    template = loader.get_template('core/consumablelist.html')
    product_categories = ProductCategory.objects.all()
    product_category_table = ProductCategoryTable(objective="consumablelist")
    product_category_subtables = product_category_table.subtables
    context = {"product_category_table" : product_category_table, "product_category_subtables" : product_category_subtables, "product_categories" : product_categories, }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def consumablelist_modify(request):
    if request.method == 'POST':
        modify_consumablelist(request)
    template = loader.get_template('core/consumablelist_modify.html')
    consumables = Consumable.objects.all()
    consumablelist = sorted(list(consumables), key=lambda t: t.id)
    units = Unit.objects.all()
    context = {"consumablelist" : consumablelist, "units" : units}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def purchases(request):
    global short_date_format
    if request.method == 'POST':
        if request.POST["form_name"] == "purchase_list_filter":
            filter_purchases(request) 
        # if request.POST["form_name"] == "transaction_entry_form":
        #     enter_new_transaction(request)
    template = loader.get_template('core/purchases.html')
    all_purchase_statuses = PurchaseStatus.objects.all()
    global selected_statuses_in_purchase_list
    global start_date_in_purchase_list
    if not start_date_in_purchase_list == None:
        start_date = start_date_in_purchase_list.strftime(short_date_format)
    else:
        start_date = ''
    global end_date_in_purchase_list
    if not end_date_in_purchase_list == None:
        end_date = end_date_in_purchase_list.strftime(short_date_format)
    else:
        end_date = ''
    global enterers_in_purchase_list
    purchases = PurchaseListTable(statuses=selected_statuses_in_purchase_list, start_date=start_date_in_purchase_list, end_date=end_date_in_purchase_list, short_date_format=short_date_format, enterers=enterers_in_purchase_list)
    purchase_enterers = []
    for p in Purchase.objects.all():
        if not p.entered_by_user in purchase_enterers:
            purchase_enterers.append(p.entered_by_user)
    context = {"all_purchase_statuses" : all_purchase_statuses, "purchases" : purchases, "purchase_enterers" : purchase_enterers, "selected_statuses_in_purchase_list" : selected_statuses_in_purchase_list,
             "start_date" : start_date, "end_date" : end_date, "selected_enterers" : enterers_in_purchase_list, }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def add_insertion(request):
    if request.method == 'POST':
        pass
    template = loader.get_template('core/add_insertion.html')
    units = Unit.objects.all()
    money_boxes = MoneyBox.objects.all()
    accounts = Account.objects.all()
    context = {"units" : units, "money_boxes" : money_boxes, "accounts" : accounts}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def general_settings(request):
    if request.method == 'POST':
        modify_general_settings(request)
    template = loader.get_template('core/general_settings.html')

    global date_format_codes
    date_formats = dict()
    for code in date_format_codes:
        date_formats[code] = datetime.date.today().strftime(code)

    context = { "group_title" : get_config("group_title"),
                "main_language" : get_config("main_language"),
                "anchor_currency" : Currency.objects.get(id=get_config("anchor_currency")),
                "all_currencies" : Currency.objects.all(), "all_time_periods" : TimePeriod.objects.all(), 
                "date_formats" : date_formats, "short_date_format" : get_config("short_date_format"), "long_date_format" : get_config("long_date_format"),
                "short_date_format_example" : datetime.date.today().strftime(get_config("short_date_format")), "long_date_format_example" : datetime.date.today().strftime(get_config("long_date_format")), 
                "single_sharings" : get_boolean_config("single_sharings"), "regular_relative_sharings" : get_boolean_config("regular_relative_sharings"), "regular_absolute_sharings" : get_boolean_config("regular_absolute_sharings"), 
                "displayed_time_period_for_membership_fees" : TimePeriod.objects.filter(singular=get_config("displayed_time_period_for_membership_fees"))[0]
                }
    return HttpResponse(template.render({**global_context(request), **context}, request))

@api_view(['GET', 'POST'])
def batches(request):
    if request.method == 'GET':
        request_no=request.GET.get('no', 1)
        batch = Batch.objects.get(no=int(request_no))
        serializer = BatchSerializer(batch, many=False)
        return Response(serializer.data)
    # elif request.method == 'POST':
    #    serializer = SnippetSerializer(data=request.data)
    #    if serializer.is_valid():
    #        serializer.save()
    #        return Response(serializer.data, status=status.HTTP_201_CREATED)
    #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def currencies(request):
    if request.method == 'GET':
        request_id=request.GET.get('id', 1)
        currency = Currency.objects.get(pk=int(request_id))
        serializer = CurrencySerializer(currency, many=False)
        return Response(serializer.data)

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer