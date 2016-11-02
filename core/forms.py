from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    batch_name = forms.CharField(disabled=True)
    #batch_no = forms.IntegerField()
    class Meta:
        model = Transaction
        fields = [
            "charged_account",
            "by_user",
            "date",
            #"batch_no",
            "batch",
            "batch_name",
            "amount",
            "comment"
        ]
        widgets = {
            'batch': forms.TextInput(attrs={'size': 6, }),
            #'batch': forms.TextInput(attrs={'size': 6, }),
        }
