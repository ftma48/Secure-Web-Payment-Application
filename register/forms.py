from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from payapp.models import Account
import requests

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    currency = forms.ChoiceField(choices=[
        ('GBP', 'British Pound'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    ])

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "currency")

    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # convert £500 to chosen currency via rest service
        currency = self.cleaned_data['currency']
        if currency == 'GBP':
            balance = 500.00
        else:
            response = requests.get(
                f'http://localhost:8000/webapps2026/conversion/GBP/{currency}/500'
            )
            balance = response.json()['converted_amount']

        # create the Account linked to this user
        Account.objects.create(user=user, balance=balance, currency=currency)
        return user