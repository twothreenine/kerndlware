from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import AccountSelectionForm, TakingForm
from .models import *
from .serializers import BatchSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
import itertools
import logging

selected_account = None
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

def global_context():
    accounts = Account.objects.all()
    context = {"accounts": accounts}
    return context

def account(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = AccountSelectionForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print("Yay " + form.cleaned_data["account"])

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AccountSelectionForm()
    account_id = 4
    template = loader.get_template('core/account.html')
    #takings = Taking.objects.filter(originator_account=account_id)
    #restitutions = Restitution.objects.filter(originator_account=account_id)
    #inpayments = Inpayment.objects.filter(originator_account=account_id)
    #depositations = Depositation.objects.filter(originator_account=account_id)
    #transfers = Transfer.objects.filter(Q(originator_account=account_id) | Q(recipient_account=account_id))
    #transactions = sorted(list(itertools.chain(takings, restitutions, inpayments, depositations, transfers)), key=lambda t: (t.date, t.id))
    # account_table = AccountTable(account_id)
    account_table = AccountTable(account_id) # [['2016-10-21', 'Taking of'],['2016-10-23', 'Taking of'],['2016-10-24', 'Taking of']]
    context = {"account_table" : account_table, "form": form}
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
