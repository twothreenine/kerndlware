from django.db.models import Q
import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import TransactionEntryForm
from .models import *
from .tables import *
from .serializers import BatchSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
import itertools
import logging

selected_account = Account.objects.get(pk=1)
logger = logging.getLogger(__name__)
selected_batch_in_batchtransactiontable = Batch.objects.get(pk=1)
selected_consumable_in_consumabletransactiontable = Consumable.objects.get(pk=1)
selected_types_in_account_transactions = TransactionType.objects.all()
start_date_in_account_transactions = models.DateField(blank=True, null=True)
start_date_in_account_transactions = None # datetime.datetime.strptime('2014-01-01' , '%Y-%m-%d')
end_date_in_account_transactions = models.DateField(blank=True, null=True)
end_date_in_account_transactions = None
enterer_in_account_transactions = models.ForeignKey('User', blank=True, null=True)
enterer_in_account_transactions = None

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
        entered_by = request.POST.get("entered_by")
        if entered_by:
            t_enterer = User.objects.get(pk=int(entered_by))
        date = request.POST.get("date")
        if date:
            t_date = datetime.datetime.strptime(date , '%Y-%m-%d').date()
        amount = request.POST.get("amount")
        if amount:
            t_amount = float(amount)
        comment = request.POST.get("comment")
        if comment:
            t_comment = str(comment)
        else:
            t_comment = ''
        if t_type.id == 1:
            batch_no = request.POST.get("batch_no")
            if batch_no:
                t_batch = Batch.objects.get(pk=int(batch_no))
            if t_date and t_amount and t_batch:
                global selected_account
                t = Taking(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment, batch=t_batch)
        elif t_type.id == 2:
            batch_no = request.POST.get("batch_no")
            if batch_no:
                t_batch = Batch.objects.get(pk=int(batch_no))
            if t_date and t_amount and t_batch:
                global selected_account
                t = Restitution(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment, batch=t_batch)
        elif t_type.id == 3:
            currency = request.POST.get("currency")
            if currency:
                t_currency = Currency.objects.get(pk=int(currency))
            else:
                t_currency = Currency.objects.get(pk=1) # get anchor currency
            money_box = request.POST.get("money_box")
            if money_box:
                t_money_box = MoneyBox.objects.get(pk=int(money_box))
            if t_date and t_amount and t_currency and t_money_box:
                global selected_account
                t = Inpayment(originator_account=selected_account, date=t_date, entered_by_user=t_enterer, amount=t_amount, comment=t_comment, currency=t_currency, money_box=t_money_box)
        # TODO: elifs for depositation and other transaction types
        t.perform()

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
    filter_account_transactions(request)
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
    users = User.objects.all()
    batches = Batch.objects.all()
    currencies = Currency.objects.all()
    money_boxes = MoneyBox.objects.all()
    context = {
        "account_table" : account_table, "deposit" : deposit,
        "taken" : taken, "entry_form" : entry_form, "entry_types" : entry_types,
        "users" : users, "currencies" : currencies, "money_boxes" : money_boxes,
        "batches" : batches, "transaction_types" : transaction_types, "selected_type_ids" : selected_type_ids, 
        "start_date" : start_date, "end_date" : end_date, "enterer_in_account_transactions" : enterer_in_account_transactions
    }
    return HttpResponse(template.render({**g_context, **context}, request))

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

def itemlist(request):
    template = loader.get_template('core/itemlist.html')
    items = Item.objects.all()
    itemlist = sorted(list(items), key=lambda t: t.id)
    context = {"itemlist" : itemlist}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def consumablelist(request):
    template = loader.get_template('core/consumablelist.html')
    consumables = Consumable.objects.all()
    consumablelist = sorted(list(consumables), key=lambda t: t.id)
    context = {"consumablelist" : consumablelist}
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

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
