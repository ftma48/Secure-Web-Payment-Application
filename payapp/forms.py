from django import forms

class SendPaymentForm(forms.Form):
    recipient_email = forms.EmailField(label="Recipient Email")
    amount = forms.DecimalField(
        label="Amount",
        max_digits=10,
        decimal_places=2,
        min_value=0.01
    )

class RequestPaymentForm(forms.Form):
    recipient_email = forms.EmailField(label="Request From (Email)")
    amount = forms.DecimalField(
        label="Amount",
        max_digits=10,
        decimal_places=2,
        min_value=0.01
    )