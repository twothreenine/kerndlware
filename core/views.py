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

try:

    if not TimePeriod.objects.all():
        day = TimePeriod(singular="day", plural="days", days=1, decimals_shown=0)
        day.save()
        week = TimePeriod(singular="week", plural="weeks", days=7, decimals_shown=1)
        week.save()
        month = TimePeriod(singular="month", plural="months", days=30.4375, decimals_shown=1)
        month.save()
        year = TimePeriod(singular="year", plural="years", days=365.25, decimals_shown=2)
        year.save()

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

    # participate/transactions list filter
    selected_types_in_account_transactions = TransactionType.objects.all()
    start_date_in_account_transactions = models.DateField(blank=True, null=True)
    start_date_in_account_transactions = None # datetime.datetime.strptime('2014-01-01' , '%Y-%m-%d')
    end_date_in_account_transactions = models.DateField(blank=True, null=True)
    end_date_in_account_transactions = None
    enterer_in_account_transactions = models.ForeignKey('User', blank=True, null=True)
    enterer_in_account_transactions = None



    # participate/transactions entry form
    default_enterer_of_new_transaction = models.ForeignKey('User', blank=True, null=True)
    default_enterer_of_new_transaction = None
    default_date_of_new_transaction = models.CharField()
    default_date_of_new_transaction = ""

    if not TransactionType.objects.all():
        """
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
        12 = Insertion (planned)
        """
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

except OperationalError:
    pass

def index(request):
    template = loader.get_template('core/index.html')

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TakingForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            taking = form.save(commit=False)
            taking.batch = Batch.objects.get(pk=int(form.cleaned_data["batch_no"]))
            taking.perform()
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TakingForm()
    
    context = {"form" : form}
    return HttpResponse(template.render(context, request))

def select_account(request):
    # account_id = 1
    if request.method == 'POST':
        account_id = request.POST.get("account_id")
        if account_id:
            account_id = int(account_id)
            global selected_account
            selected_account = Account.objects.get(pk=account_id)

def select_batch_for_batchtransactiontable(request):
    if request.method == 'POST':
        batch_id = request.POST.get("batch_id")
        if batch_id:
            batch_id = int(batch_id)
            global selected_batch_in_batchtransactiontable
            selected_batch_in_batchtransactiontable = Batch.objects.get(pk=batch_id)

def select_consumable_for_consumabletransactiontable(request):
    if request.method == 'POST':
        consumable_id = request.POST.get("consumable_id")
        if consumable_id:
            consumable_id = int(consumable_id)
            global selected_consumable_in_consumabletransactiontable
            selected_consumable_in_consumabletransactiontable = Consumable.objects.get(pk=consumable_id)

def filter_account_transactions(request):
    if request.method == 'POST':
        transaction_types = request.POST.getlist("transaction_type")
        global selected_types_in_account_transactions
        selected_types_in_account_transactions = []
        if transaction_types:
            for t in transaction_types:
                t = int(t)
                tt = TransactionType.objects.get(pk=t)
                selected_types_in_account_transactions.append(tt)
        start_date = request.POST.get("start_date")
        global start_date_in_account_transactions
        if start_date:
            start_date_in_account_transactions = datetime.datetime.strptime(start_date , '%Y-%m-%d').date()
        else:
            start_date_in_account_transactions = None
        end_date = request.POST.get("end_date")
        global end_date_in_account_transactions
        if end_date:
            end_date_in_account_transactions = datetime.datetime.strptime(end_date , '%Y-%m-%d').date()
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
    if request.method == 'POST':
        transaction_type = request.POST.get("type")
        if transaction_type:
            t_type = TransactionType.objects.get(pk=int(transaction_type))
        else:
            t_type = None
        entered_by = request.POST.get("entered_by")
        if entered_by:
            t_enterer = User.objects.get(pk=int(entered_by))
            global default_enterer_of_new_transaction
            default_enterer_of_new_transaction = t_enterer
            global recent_users
            i = recent_users.index(t_enterer)
            recent_users.insert(0, recent_users.pop(i))
        date = request.POST.get("date")
        if date:
            t_date = datetime.datetime.strptime(date , '%Y-%m-%d').date()
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
            if t_type.id == 1: # taking
                batch_no = request.POST.get("batch_no")
                if batch_no:
                    t_batch = Batch.objects.get(pk=int(batch_no))
                if t_date and t_amount and t_batch:
                    t = Taking(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment, batch=t_batch)
                    t.perform()
            elif t_type.id == 2: # restitution
                batch_no = request.POST.get("batch_no")
                if batch_no:
                    t_batch = Batch.objects.get(pk=int(batch_no))
                if t_date and t_amount and t_batch:
                    t = Restitution(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment, batch=t_batch)
                    t.perform()
            elif t_type.id == 3: # inpayment
                currency = request.POST.get("currency")
                if currency:
                    t_currency = Currency.objects.get(pk=int(currency))
                else:
                    t_currency = Currency.objects.get(pk=1) # get anchor currency
                money_box = request.POST.get("money_box")
                if money_box:
                    t_money_box = MoneyBox.objects.get(pk=int(money_box))
                if t_date and t_amount and t_currency and t_money_box:
                    t = Inpayment(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment, currency=t_currency, money_box=t_money_box)
                    t.perform()
            elif t_type.id == 4: # depositation
                currency = request.POST.get("currency")
                if currency:
                    t_currency = Currency.objects.get(pk=int(currency))
                else:
                    t_currency = Currency.objects.get(pk=1) # get anchor currency
                money_box = request.POST.get("money_box")
                if money_box:
                    t_money_box = MoneyBox.objects.get(pk=int(money_box))
                if t_date and t_amount and t_currency and t_money_box:
                    t = Depositation(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment, currency=t_currency, money_box=t_money_box)
                    t.perform()
            elif t_type.id == 7: # transfer
                recipient_account = request.POST.get("recipient_account")
                if recipient_account:
                    t_recipient_account = Account.objects.get(pk=int(recipient_account))
                if t_date and t_amount and t_recipient_account:
                    t = Transfer(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment, recipient_account=t_recipient_account)
                    t.perform()
            elif t_type.id == 8 or t_type.id == 9 or t_type.id == 10 or t_type.id == 11: # cost sharing, proceeds sharing, donation, recovery
                participating_accounts = request.POST.getlist("participating_accounts")
                t_participating_accounts = []
                if participating_accounts:
                    for p in participating_accounts:
                        pa = Account.objects.get(pk=int(p))
                        t_participating_accounts.append(pa)
                if t_date and t_amount and t_participating_accounts:
                    if t_type.id == 8:
                        t = CostSharing(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment)
                    if t_type.id == 9:
                        t = ProceedsSharing(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment)
                    if t_type.id == 10:
                        t = Donation(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment)
                    if t_type.id == 11:
                        t = Recovery(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment)
                    t.save()
                    t.perform(transaction_type_id=t_type.id, participating_accounts=t_participating_accounts)

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
        selected_account.users.clear()
        for us in request.POST.getlist("users"):
            us = User.objects.get(pk=int(us))
            us.accounts.add(selected_account)
            us.save()
            selected_account.users.add(us)
        if not request.POST.get("new_user") == '':
            if request.POST.get("is_non_real"):
                u = VirtualUser(name=str(request.POST.get("new_user")))
            else:
                u = Person(name=str(request.POST.get("new_user")), last_name='', first_name='')
            u.save()
            u.accounts.add(selected_account)
            u.save()
            selected_account.users.add(u)
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

def global_context(request):
    accounts = Account.objects.all()
    global selected_account
    balance = selected_account.balance_str
    current_path = request.get_full_path()
    context = {"accounts": accounts, "balance" : balance, "selected_account" : selected_account, "current_path" : current_path, }
    return context

def base(request):
    select_account(request)
    return HttpResponseRedirect(request.POST['current_path'])

def account(request):
    if request.method == 'POST':
        if request.POST["form_name"] == "transaction_list_filter":
            filter_account_transactions(request) 
        if request.POST["form_name"] == "transaction_entry_form":
            enter_new_transaction(request)
    template = loader.get_template('core/account.html')
    g_context = global_context(request)
    global selected_account
    deposit = selected_account.deposit_str
    taken = selected_account.taken_str
    transaction_types = TransactionType.objects.all()
    global selected_types_in_account_transactions
    selected_type_ids = []
    for ttype in selected_types_in_account_transactions:
        selected_type_ids.append(ttype.id)
    global start_date_in_account_transactions
    if not start_date_in_account_transactions == None:
        start_date = start_date_in_account_transactions.strftime("%Y-%m-%d")
    else:
        start_date = ''
    global end_date_in_account_transactions
    if not end_date_in_account_transactions == None:
        end_date = end_date_in_account_transactions.strftime("%Y-%m-%d")
    else:
        end_date = ''
    global enterer_in_account_transactions
    transactions = Transaction.objects.all()
    account_table = AccountTable(account_id = selected_account.id, types = selected_types_in_account_transactions, start_date = start_date_in_account_transactions, end_date = end_date_in_account_transactions, 
                                enterer = enterer_in_account_transactions)
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
    global recent_users
    users_of_selected_account = []
    recent_other_users = []
    for user in recent_users:
        if user.accounts.filter(id=selected_account.id).count(): # if selected_account is an account related to user
            users_of_selected_account.append(user)
        else:
            recent_other_users.append(user)

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
    global default_enterer_of_new_transaction
    context = {
        "account_table" : account_table, "deposit" : deposit,
        "taken" : taken, "entry_form" : entry_form, "entry_types" : entry_types,
        "currencies" : currencies, "money_boxes" : money_boxes,
        "batches" : batches, "transaction_types" : transaction_types, "selected_type_ids" : selected_type_ids, 
        "start_date" : start_date, "end_date" : end_date, "enterer_in_account_transactions" : enterer_in_account_transactions,
        "accounts_except_itself" : accounts_except_itself, "accounts" : accounts, "users_of_selected_account" : users_of_selected_account, "recent_other_users" : recent_other_users,
        "table_users_of_selected_account" : table_users_of_selected_account, "other_table_users" : other_table_users, 
        "default_date_of_new_transaction" : default_date_of_new_transaction, "default_enterer_of_new_transaction" : default_enterer_of_new_transaction, 
    }
    return HttpResponse(template.render({**g_context, **context}, request))

def register(request):
    create_account(request)
    template = loader.get_template('core/register.html')
    global selected_account
    users = User.objects.all()
    context = {"account" : selected_account, "users" : users}
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

def account_settings(request):
    modify_account(request)
    template = loader.get_template('core/account_settings.html')
    global selected_account
    users = User.objects.all()
    context = {"account" : selected_account, "users" : users}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def suppliers(request):
    # modify_supplier(request) # TODO
    template = loader.get_template('core/suppliers.html')
    supplier_table = SupplierTable()
    context = {"supplier_table" : supplier_table }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def transactionlist(request):
    template = loader.get_template('core/transactionlist.html')
    transaction_table = TransactionTable()
    context = {"transaction_table" : transaction_table}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def batchtransactiontable(request):
    select_batch_for_batchtransactiontable(request)
    global selected_batch_in_batchtransactiontable
    batch_transaction_table = BatchTransactionTable(selected_batch_in_batchtransactiontable.id)
    batches = Batch.objects.all()
    stock = selected_batch_in_batchtransactiontable.unit.display(selected_batch_in_batchtransactiontable.calc_stock(), show_contents=False)
    price = selected_batch_in_batchtransactiontable.price_str_long()
    unit_weight = selected_batch_in_batchtransactiontable.unit.unit_weight(selected_batch_in_batchtransactiontable)
    template = loader.get_template('core/batchtransactiontable.html')
    context = {"batches" : batches, "stock" : stock, "batch_transaction_table" : batch_transaction_table, "selected_batch_in_batchtransactiontable" : selected_batch_in_batchtransactiontable, "unit_weight" : unit_weight, "price" : price, }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def consumabletransactiontable(request):
    select_consumable_for_consumabletransactiontable(request)
    global selected_consumable_in_consumabletransactiontable
    consumable_transaction_table = ConsumableTransactionTable(selected_consumable_in_consumabletransactiontable.id)
    consumables = Consumable.objects.all()
    stock = selected_consumable_in_consumabletransactiontable.unit.display(selected_consumable_in_consumabletransactiontable.calc_stock())
    unit_weight = selected_consumable_in_consumabletransactiontable.unit.unit_weight(selected_consumable_in_consumabletransactiontable)
    template = loader.get_template('core/consumabletransactiontable.html')
    context = {"consumables" : consumables, "stock" : stock, "consumable_transaction_table" : consumable_transaction_table, "selected_consumable_in_consumabletransactiontable" : selected_consumable_in_consumabletransactiontable, "unit_weight" : unit_weight, }
    return HttpResponse(template.render({**global_context(request), **context}, request))

def accountlist(request):
    g_context = global_context(request)
    template = loader.get_template('core/accountlist.html')
    accounts = Account.objects.all()
    accountlist = sorted(list(accounts), key=lambda t: t.id)
    context = {"accountlist" : accountlist}
    return HttpResponse(template.render({**g_context, **context}, request))

def batchlist(request):
    template = loader.get_template('core/batchlist.html')
    batches = Batch.objects.all()
    batchlist = sorted(list(batches), key=lambda t: t.id)
    context = {"batchlist" : batchlist}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def batchlist_modify(request):
    template = loader.get_template('core/batchlist_modify.html')
    batches = Batch.objects.all()
    batchlist = sorted(list(batches), key=lambda t: t.id)
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

@api_view(['GET', 'POST'])
def batches(request):
    if request.method == 'GET':
        request_id=request.GET.get('id', 1)
        batch = Batch.objects.get(pk=int(request_id))
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
