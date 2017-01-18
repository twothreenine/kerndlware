from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
# from .forms import TakingForm
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

def global_context(request):
    select_account(request)
    accounts = Account.objects.all()
    global selected_account
    balance = "{} €".format(format(selected_account.balance, '.2f'))
    context = {"accounts": accounts, "balance" : balance, "selected_account" : selected_account}
    return context

def account(request):
    template = loader.get_template('core/account.html')
    g_context = global_context(request)
    global selected_account
    account_table = AccountTable(account_id=selected_account.id)
    deposit = "{} €".format(format(selected_account.deposit, '.2f'))
    taken = "{} kg".format(format(selected_account.taken, '.1f'))
    context = {"account_table" : account_table, "deposit" : deposit, "taken" : taken}
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
    stock = selected_batch_in_batchtransactiontable.unit.display(selected_batch_in_batchtransactiontable.calc_stock())
    template = loader.get_template('core/batchtransactiontable.html')
    context = {"batches" : batches, "stock" : stock, "batch_transaction_table" : batch_transaction_table, "selected_batch_in_batchtransactiontable" : selected_batch_in_batchtransactiontable}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def consumabletransactiontable(request):
    select_consumable_for_consumabletransactiontable(request)
    global selected_consumable_in_consumabletransactiontable
    consumable_transaction_table = ConsumableTransactionTable(selected_consumable_in_consumabletransactiontable.id)
    consumables = Consumable.objects.all()
    stock = selected_consumable_in_consumabletransactiontable.unit.display(selected_consumable_in_consumabletransactiontable.calc_stock())
    template = loader.get_template('core/consumabletransactiontable.html')
    context = {"consumables" : consumables, "stock" : stock, "consumable_transaction_table" : consumable_transaction_table, "selected_consumable_in_consumabletransactiontable" : selected_consumable_in_consumabletransactiontable}
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
    #elif request.method == 'POST':
    #    serializer = SnippetSerializer(data=request.data)
    #    if serializer.is_valid():
    #        serializer.save()
    #        return Response(serializer.data, status=status.HTTP_201_CREATED)
    #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
