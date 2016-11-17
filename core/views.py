from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import TakingForm
from .models import Batch, Taking, Restitution, Inpayment, Depositation
from .serializers import BatchSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

import itertools

def index(request):
    template = loader.get_template('core/index.html')

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TakingForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            taking = form.save()
            taking.perform()
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TakingForm()
        
    context = {"form" : form}
    return HttpResponse(template.render(context, request))

def account(request):
    account_id = 4
    template = loader.get_template('core/account.html')
    takings = Taking.objects.filter(charged_account=account_id)
    restitutions = Restitution.objects.filter(charged_account=account_id)
    inpayments = Inpayment.objects.filter(charged_account=account_id)
    depositations = Depositation.objects.filter(charged_account=account_id)
    transactions = sorted(list(itertools.chain(takings, restitutions, inpayments, depositations)), key=lambda t: (t.date, t.id))
    context = {"transactions" : transactions}
    return HttpResponse(template.render(context, request))

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
