from django import forms

form .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "charged_user",
            "typing_user",
            "date",
            "good",
            "amount",
            "comment"
        ]
