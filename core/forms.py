from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "charged_account",
            "by_user",
            "date",
            "batch",
            "amount",
            "comment"
        ]
