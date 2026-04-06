import requests
import base64
from datetime import datetime
from django.conf import settings


from datetime import datetime
import requests
import base64

def format_phone(phone):
    phone = phone.strip()
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]
    return phone

def get_access_token():
    url = f"{settings.BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    print("TOKEN RESPONSE:", response.text)
    return response.json().get("access_token")

def generate_password():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode("utf-8")
    return password, timestamp

def stk_push(phone, amount, account_reference):
    phone = format_phone(phone)
    access_token = get_access_token()
    password, timestamp = generate_password()

    url = f"{settings.BASE_URL}/mpesa/stkpush/v1/processrequest"

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": "Room Booking Payment"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print("STK FULL RESPONSE:", response.text)
    return response.json()