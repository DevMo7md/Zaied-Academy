from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Subscription
from LP_app.models import *
from datetime import datetime, timedelta
from django.utils import timezone
import requests
from django.conf import settings
from .payment_manager import PaymobCardManager
from LP_app.models import *
#handle callback using django
import hmac
import hashlib
import json
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import *


@login_required
def subscribe(request):
    if request.method == 'POST':
        
        paymob_manager = PaymobCardManager()
        integration_id = 4602060  # Your Payment Integration id to spicify what payment is it like (cards, or mobile wallet, etc..)
        amount = 120  # amount that you want the user to pay
        currency = "EGP"  # currency USD or EGP , etc..
        user_name = User.objects.get(id=request.user.id)
        student = Student.objects.get(user__id=request.user.id)
        paymentKey, orderId = paymob_manager.getPaymentKey(
                amount=amount, 
                currency=currency, 
                integration_id=integration_id, 
                email=request.user.email, 
                phone_number=student.phone_num, 
                first_name=user_name.first_name,
                last_name=user_name.last_name,
                )
        order = Order.objects.create(
            user = request.user,
            paymob_order_id = orderId,

        )
        payment_url = f"https://accept.paymob.com/api/acceptance/iframes/853728?payment_token={paymentKey}"

        
        return redirect(payment_url)

    return render(request, 'Subscription/subscribe.html')


def extract_value(data, keys):
    """Extract a nested value from a dictionary using a list of keys."""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, '')
        else:
            return ''
    return data

def calc_hmac(request_data, hmac_secret):
    # Define the field paths
    fields = [
        ('obj', 'amount_cents'),
        ('obj', 'created_at'),
        ('obj', 'currency'),
        ('obj', 'error_occured'),
        ('obj', 'has_parent_transaction'),
        ('obj', 'id'),
        ('obj', 'integration_id'),
        ('obj', 'is_3d_secure'),
        ('obj', 'is_auth'),
        ('obj', 'is_capture'),
        ('obj', 'is_refunded'),
        ('obj', 'is_standalone_payment'),
        ('obj', 'is_voided'),
        ('obj', 'order', 'id'),
        ('obj', 'owner'),
        ('obj', 'pending'),
        ('obj', 'source_data', 'pan'),
        ('obj', 'source_data', 'sub_type'),
        ('obj', 'source_data', 'type'),
        ('obj', 'success'),
    ]

    # Extract values
    values = {}
    for path in fields:
        value = extract_value(request_data, path)
        if isinstance(value, bool):
            value = "true" if value else "false"
        values[':'.join(path)] = str(value)

    # Concatenate the values
    concatenated_string = ''.join(values.values())
    

    # Generate the HMAC
    hmac_generated = hmac.new(hmac_secret.encode(), concatenated_string.encode(), hashlib.sha512).hexdigest()
    return hmac_generated







@csrf_exempt
def processed_callback(request):
    if request.method == 'POST':
        # Parse the JSON body of the request
        request_data = json.loads(request.body)
        
        # Your HMAC secret
        hmac_secret = settings.PAYMOB_HMAC 
        
        # Calculate the HMAC using the provided data
        generated_hmac = calc_hmac(request_data, hmac_secret)

        # Get the received HMAC from query parameters
        hmac_received = request.GET.get('hmac')
    

        if generated_hmac == hmac_received:
            # Process the transaction as needed
            success_status = extract_value(request_data, ['obj', 'success'])
            order_id = extract_value(request_data, ('obj', 'order', 'id'))
            print(f"Payment Success Status: {success_status}, order_id: {order_id}")
            if success_status == True:
                # Handle successful payment
                order = Order.objects.get(paymob_order_id=order_id)
                order.completed = True
                order.save()
                user = order.user
                subscription, created = Subscription.objects.get_or_create(user=user)
                subscription.start_date = timezone.now() + timedelta(hours=2)  
                subscription.end_date = subscription.start_date + timedelta(days=30)
                subscription.save()
                student = Student.objects.get(user=user)
                student.subscription_active = True
                student.save()

                return redirect('home')

            else:
                # Handle failed payment
                messages.error(request, 'Something went wrong. Please try again.')
                return redirect('home')

        else:
            print("HMAC validation failed")
            messages.error(request, 'Invalid HMAC validation.')
            return redirect('home')








def response_extract_value(data, path):
    """
    Extracts a value from a dictionary using a path.
    For the updated structure, paths are flat and directly match keys in the dictionary.
    """
    # Directly get the value for the path
    value = data.get(path, "")
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)

def response_calc_hmac(request_data, hmac_secret):
    """
    Calculate the HMAC for the given request data.
    """
    # Define the field paths
    fields = [
        'amount_cents',
        'created_at',
        'currency',
        'error_occured',
        'has_parent_transaction',
        'id',
        'integration_id',
        'is_3d_secure',
        'is_auth',
        'is_capture',
        'is_refunded',
        'is_standalone_payment',
        'is_voided',
        'order',
        'owner',
        'pending',
        'source_data.pan',
        'source_data.sub_type',
        'source_data.type',
        'success',
    ]

    # Extract values
    values = []
    for field in fields:
        value = response_extract_value(request_data, field)
        values.append(value)
        # Print for debugging
        #print(f"Field: {field}, Value: {value}")

    # Concatenate the values
    concatenated_string = ''.join(values)
    

    # Generate the HMAC
    hmac_generated = hmac.new(hmac_secret.encode(), concatenated_string.encode(), hashlib.sha512).hexdigest()
    return hmac_generated

@csrf_exempt
def order_success(request):
    if request.method == 'GET':  # Assuming the data is being sent via a GET request
        # Parse the query parameters
        query_params = request.GET.dict()

        # Your HMAC secret
        hmac_secret = settings.PAYMOB_HMAC 
        
        generated_hmac = response_calc_hmac(query_params, hmac_secret)

        # Get the received HMAC from query parameters
        hmac_received = query_params.get('hmac')
        if generated_hmac == hmac_received:
            # Process the transaction as needed
            success_status = query_params.get('success')
            order_id = query_params.get('order')
            print(f"Payment Success Status: {success_status}, order_id: {order_id}")
            
            if success_status == 'true':
               
                return redirect('home')

            else:
                # Handle failed payment
                messages.error(request, 'Something went wrong. Please try again.')
                return redirect('home')

        else:
            print("HMAC validation failed")
            messages.error(request, 'Invalid HMAC validation.')
            return redirect('home')