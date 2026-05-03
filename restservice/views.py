from django.shortcuts import render
from django.http import JsonResponse

RATES = {
    'GBP': 1.0,
    'USD': 1.36,
    'EUR': 1.16,
}


def conversion(request, currency1, currency2, amount):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if currency1 not in RATES or currency2 not in RATES:
        return JsonResponse({'error': 'Unsupported currency'}, status=400)

    rate = RATES[currency2] / RATES[currency1]
    converted = round(float(amount) * rate, 2)

    return JsonResponse({'rate': rate, 'converted_amount': converted})