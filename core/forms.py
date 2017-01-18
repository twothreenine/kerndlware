from django import forms
# from .models import Taking

class TransactionEntryForm(forms.Form):

    # Generic fields
    transaction_type = forms.CharField()
    by_user = forms.IntegerField()
    date = forms.DateField()
    amount = forms.FloatField()
    value = forms.CharField(widget=forms.TextInput(attrs={"readonly": "true"}))
    comment = forms.CharField()

    # Taking & restitution fields
    batch_no = forms.IntegerField()
    batch_name = forms.CharField(widget=forms.TextInput(attrs={"readonly": "true"}))

    # Inpayment & depositation
    moneybox = forms.IntegerField()
    currency = forms.IntegerField()

# class TakingForm(forms.ModelForm):
#     batch_name = forms.CharField(disabled=True, required=False)
#     batch_no = forms.IntegerField()
#     class Meta:
#         model = Taking
#         fields = [
#             "originator_account",
#             "entered_by_user",
#             "date",
#             "batch_no",
#             #"batch",
#             "batch_name",
#             "amount",
#             "comment"
#         ]
#         #widgets = {
#             #'batch': forms.TextInput(attrs={'size': 6, }),
#             #'batch': forms.TextInput(attrs={'size': 6, }),
#         #}

#     #def __init__(self, *args, **kwargs):
#         #super(TakingForm, self).__init__(*args, **kwargs)
#         #self.fields['batch'].label = "Batch no"
