from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import transaction
from payapp.models import Account, Transaction, PaymentRequest, Notification
from payapp.forms import SendPaymentForm, RequestPaymentForm
import requests as http_requests
from decimal import Decimal
from register.forms import RegisterForm

# payments/requests

@login_required(login_url='/webapps2026/register/login/')
def index(request):
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(
        sender=request.user
    ) | Transaction.objects.filter(
        recipient=request.user
    )
    transactions = transactions.order_by('-timestamp')
    return render(request, 'payapp/index.html', {
        'account': account,
        'transactions': transactions,
    })

@login_required(login_url='/webapps2026/register/login/')
def send_payment(request):
    if request.method == 'POST':
        form = SendPaymentForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            amount = form.cleaned_data['amount']

            try:
                recipient = User.objects.get(email=recipient_email)
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")
                return render(request, 'payapp/sendpayment.html', {'form': form})

            if recipient == request.user:
                messages.error(request, "You cannot send money to yourself.")
                return render(request, 'payapp/sendpayment.html', {'form': form})

            try:
                with transaction.atomic():
                    sender_account = Account.objects.select_for_update().get(user=request.user)
                    recipient_account = Account.objects.select_for_update().get(user=recipient)

                    # check funds
                    if sender_account.balance < amount:
                        messages.error(request, "Insufficient funds.")
                        return render(request, 'payapp/sendpayment.html', {'form': form})

                    # convert amount if diff currency
                    if sender_account.currency != recipient_account.currency:
                        response = http_requests.get(
                            f'http://localhost:8000/webapps2026/conversion/'
                            f'{sender_account.currency}/{recipient_account.currency}/{amount}'
                        )
                        converted_amount = Decimal(str(response.json()['converted_amount']))
                    else:
                        converted_amount = amount

                    sender_account.balance -= amount
                    recipient_account.balance += converted_amount
                    sender_account.save()
                    recipient_account.save()

                    Transaction.objects.create(
                        sender=request.user,
                        recipient=recipient,
                        amount=amount,
                        currency=sender_account.currency,
                        transaction_type='payment'
                    )

                messages.success(request, f"Successfully sent {amount} {sender_account.currency} to {recipient.username}.")

                # notify the recipient
                Notification.objects.create(
                    user=recipient,
                    message=f"{request.user.username} sent you {amount} {sender_account.currency}."
                )
                return redirect('index')


            except Exception as e:

                messages.error(request, f"Payment failed: {str(e)}")

    else:
        form = SendPaymentForm()

    return render(request, 'payapp/sendpayment.html', {'form': form})

@login_required(login_url='/webapps2026/register/login/')
def request_payment(request):
    if request.method == 'POST':
        form = RequestPaymentForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            amount = form.cleaned_data['amount']

            # check user exists
            try:
                requestee = User.objects.get(email=recipient_email)
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")
                return render(request, 'payapp/requestpayment.html', {'form': form})

            if requestee == request.user:
                messages.error(request, "You cannot request money from yourself.")
                return render(request, 'payapp/requestpayment.html', {'form': form})

            # save request
            PaymentRequest.objects.create(
                requester=request.user,
                requestee=requestee,
                amount=amount,
                currency=Account.objects.get(user=request.user).currency,
                status='pending'
            )
            messages.success(request, f"Payment request sent to {requestee.username}.")

            # notify the requestee
            Notification.objects.create(
                user=requestee,
                message=f"{request.user.username} requested {amount} {Account.objects.get(user=request.user).currency} from you."
            )

            return redirect('index')
    else:
        form = RequestPaymentForm()

    return render(request, 'payapp/requestpayment.html', {'form': form})


@login_required(login_url='/webapps2026/register/login/')
def notifications(request):
    incoming = PaymentRequest.objects.filter(requestee=request.user, status='pending')
    outgoing = PaymentRequest.objects.filter(requester=request.user).order_by('-timestamp')

    # get all notifs and mark them as read
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-timestamp')
    user_notifications.update(is_read=True)

    return render(request, 'payapp/notifications.html', {
        'incoming': incoming,
        'outgoing': outgoing,
        'user_notifications': user_notifications,
    })


@login_required(login_url='/webapps2026/register/login/')
def handle_request(request, request_id):
    payment_request = PaymentRequest.objects.get(id=request_id, requestee=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'accept':
            try:
                with transaction.atomic():
                    sender_account = Account.objects.select_for_update().get(user=request.user)
                    recipient_account = Account.objects.select_for_update().get(user=payment_request.requester)

                    if sender_account.balance < payment_request.amount:
                        messages.error(request, "Insufficient funds.")
                        return redirect('notifications')

                    # convert if diff currwency
                    if sender_account.currency != recipient_account.currency:
                        response = http_requests.get(
                            f'http://localhost:8000/webapps2026/conversion/'
                            f'{sender_account.currency}/{recipient_account.currency}/{payment_request.amount}'
                        )
                        converted_amount = Decimal(str(response.json()['converted_amount']))
                    else:
                        converted_amount = payment_request.amount

                    sender_account.balance -= payment_request.amount
                    recipient_account.balance += converted_amount
                    sender_account.save()
                    recipient_account.save()

                    Transaction.objects.create(
                        sender=request.user,
                        recipient=payment_request.requester,
                        amount=payment_request.amount,
                        currency=sender_account.currency,
                        transaction_type='payment'
                    )

                    payment_request.status = 'accepted'
                    payment_request.save()

                messages.success(request, "Payment request accepted.")
                # notify the requester their request was accepted
                Notification.objects.create(
                    user=payment_request.requester,
                    message=f"{request.user.username} accepted your payment request of {payment_request.amount} {payment_request.currency}."
                )

            except Exception as e:
                messages.error(request, f"Payment failed: {str(e)}")

        elif action == 'reject':
            payment_request.status = 'rejected'
            payment_request.save()
            messages.info(request, "Payment request rejected.")

            # notify of rejection
            Notification.objects.create(
                user=payment_request.requester,
                message=f"{request.user.username} rejected your payment request of {payment_request.amount} {payment_request.currency}."
            )

    return redirect('notifications')

# admin funcs

def admin_check(request):
    # is user logged in and staff
    return request.user.is_authenticated and request.user.is_staff


@login_required(login_url='/webapps2026/register/login/')
def admin_users(request):
    # redirect non-admins
    if not admin_check(request):
        messages.error(request, "Access denied.")
        return redirect('index')

    # get all users
    users = User.objects.all().order_by('username')
    user_accounts = []
    for u in users:
        try:
            account = Account.objects.get(user=u)
        except Account.DoesNotExist:
            account = None
        user_accounts.append((u, account))

    return render(request, 'payapp/adminusers.html', {'user_accounts': user_accounts})


@login_required(login_url='/webapps2026/register/login/')
def admin_transactions(request):
    # redirect non-admins
    if not admin_check(request):
        messages.error(request, "Access denied.")
        return redirect('index')

    # get all transactions
    all_transactions = Transaction.objects.all().order_by('-timestamp')
    return render(request, 'payapp/admintransactions.html', {'transactions': all_transactions})


@login_required(login_url='/webapps2026/register/login/')
def admin_register(request):
    if not admin_check(request):
        messages.error(request, "Access denied.")
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            messages.success(request, f"Admin {user.username} created successfully.")
            return redirect('admin_users')
        messages.error(request, "Invalid form data.")
    else:
        form = RegisterForm()

    return render(request, 'payapp/adminregister.html', {'form': form})