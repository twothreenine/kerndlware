from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import TakingForm
from .models import *
from .serializers import BatchSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
import itertools
import logging

selected_account = Account.objects.get(pk=1)
logger = logging.getLogger(__name__)

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
    if request.method == 'POST':
        account_id = request.POST.get("account_id")
        if account_id:
            account_id = int(account_id)
    if account_id == None:
        account_id = 1

    global selected_account
    selected_account = Account.objects.get(pk=account_id)

def global_context(request):
    select_account(request)
    accounts = Account.objects.all()
    balance = "test €" # "{} €".format(format(Account.objects.get(pk=account_id).balance, '.2f')) # account_id has to be known from drop down menu
    #balance = "{} €".format(format(Account.objects.get(pk=account_id).balance, '.2f'))
    #form = account_selection_form(request)
    global selected_account
    context = {"accounts": accounts, "balance" : balance, "selected_account" : selected_account}
    return context

def account(request):
    template = loader.get_template('core/account.html')
    g_context = global_context(request)
    global selected_account
    account_table = AccountTable(selected_account.id) # [['2016-10-21', 'Taking of'],['2016-10-23', 'Taking of'],['2016-10-24', 'Taking of']]
    deposit = "{} €".format(format(Account.objects.get(pk=selected_account.id).deposit, '.2f'))
    taken = "{} kg".format(format(Account.objects.get(pk=selected_account.id).taken, '.2f'))
    context = {"account_table" : account_table, "deposit" : deposit, "taken" : taken}
    return HttpResponse(template.render({**g_context, **context}, request))

def transactionlist(request):
    template = loader.get_template('core/transactionlist.html')
    transaction_table = TransactionTable()
    context = {"transaction_table" : transaction_table}
    return HttpResponse(template.render({**global_context(request), **context}, request))

def batchtransactiontable(request):
    batches = Batch.objects.all()
    batch_id = 3
    stock = Batch.objects.get(pk=batch_id).stock
    template = loader.get_template('core/batchtransactiontable.html')
    batch_transaction_table = BatchTransactionTable(batch_id)
    context = {"batches" : batches, "stock" : stock, "batch_transaction_table" : batch_transaction_table}
    return HttpResponse(template.render({**global_context(), **context}, request))

def consumabletransactiontable(request):
    consumables = Consumable.objects.all()
    consumable_id = 2
    stock = Consumable.objects.get(pk=consumable_id).stock
    template = loader.get_template('core/consumabletransactiontable.html')
    consumable_transaction_table = ConsumableTransactionTable(consumable_id)
    context = {"consumables" : consumables, "stock" : stock, "consumable_transaction_table" : consumable_transaction_table}
    return HttpResponse(template.render({**global_context(), **context}, request))

def accountlist(request):
    template = loader.get_template('core/accountlist.html')
    accounts = Account.objects.all()
    accountlist = sorted(list(accounts), key=lambda t: t.id)
    context = {"accountlist" : accountlist}
    return HttpResponse(template.render({**global_context(), **context}, request))

def batchlist(request):
    template = loader.get_template('core/batchlist.html')
    batches = Batch.objects.all()
    batchlist = sorted(list(batches), key=lambda t: t.id)
    context = {"batchlist" : batchlist}
    return HttpResponse(template.render({**global_context(), **context}, request))

def itemlist(request):
    template = loader.get_template('core/itemlist.html')
    items = Item.objects.all()
    itemlist = sorted(list(items), key=lambda t: t.id)
    context = {"itemlist" : itemlist}
    return HttpResponse(template.render({**global_context(), **context}, request))

def consumablelist(request):
    template = loader.get_template('core/consumablelist.html')
    consumables = Consumable.objects.all()
    consumablelist = sorted(list(consumables), key=lambda t: t.id)
    context = {"consumablelist" : consumablelist}
    return HttpResponse(template.render({**global_context(), **context}, request))

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
