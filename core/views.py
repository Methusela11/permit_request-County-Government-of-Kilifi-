from django.contrib import messages
from .models import PermitRequest, ClientMessage
import base64
import requests
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def home(request):
    return render(request, 'index.html')

@login_required
def noisepermit(request):
    return render(request, 'noisepermitform.html')

@login_required
def treepermit(request):
    return render(request, 'treepermitform.html')

@login_required
def forestpermit(request):
    return render(request, 'forestpermitform.html')

from django.shortcuts import render, redirect
from .models import PermitRequest

def submitpermit(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        id_number = request.POST['id_number']
        phone = request.POST['phone']
        subcounty = request.POST['subcounty']
        ward = request.POST['ward']
        location = request.POST['location']
        purpose = request.POST['purpose']
        source = request.POST['source']
        date = request.POST['date']
        time = request.POST['time']

        PermitRequest.objects.create(
            full_name=full_name,
            id_number=id_number,
            phone=phone,
            subcounty=subcounty,
            ward=ward,
            location=location,
            purpose=purpose,
            source=source,
            date=date,
            time=time
        )
    return redirect('checkapproval', id_number=request.POST['id_number'])

def check_approval(request, id_number):
    try:
        permit = PermitRequest.objects.filter(id_number=id_number).latest('submitted_at')
    except PermitRequest.DoesNotExist:
        return render(request, 'approval_status.html', {'error': 'No request found for this ID.'})

    if permit.approved:
        return redirect('thankyou')
    else:
        return render(request, 'approval_status.html', {
            'permit': permit,
            'waiting': True
        })

def check_permit_status(request):
    latest_request = PermitRequest.objects.filter(phone=request.user.username).order_by('-submitted_at').first()

    if latest_request and latest_request.approved:
        return redirect('thankyou')  # Redirect if approved
    else:
        return render(request, 'approval_status.html', {'permit': latest_request})

def thankyou(request):
    return render(request, "thankyou.html")

def requestednoisepermits(request):
    permits = PermitRequest.objects.filter(is_approved=True).order_by('-submitted_at')
    return render(request, 'requestednoisepermits.html', {'permits': permits})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['emailaddress']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('signup')

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password1)
        )

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')

def loginn(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Replace 'login' with your login URL name

@login_required
def permitss(request):
    return render(request, "permits.html")

@csrf_protect
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('client_name', '')
        email = request.POST.get('client_email')
        message = request.POST.get('client_message')

        ClientMessage.objects.create(
            client_name=name,
            client_email=email,
            client_message=message
        )
        messages.success(request, "Thank you for contacting us.")
        return redirect('/contact/')  # Or a 'success' page if preferred

    return render(request, 'contact.html')

def clientss(request):
    clients = ClientMessage.objects.all().order_by('-filled_at')
    return render(request, 'clients.html', {'clients': clients})

def readmore(request):
    return render(request, "about.html")

def permit_report(request):
    permits = PermitRequest.objects.all()
    subcounty = request.GET.get('subcounty')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if subcounty:
        permits = permits.filter(subcounty=subcounty)

    if status:
        if status == "approved":
            permits = permits.filter(approved=True)
        elif status == "pending":
            permits = permits.filter(approved=False)

    if start_date and end_date:
        permits = permits.filter(date__range=[start_date, end_date])

    return render(request, 'permit_report.html', {
        'permits': permits,
    })


@csrf_exempt
def submit_permit_payment(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        amount = 10  # You can later change this dynamically
        messages.success(request, "Your details have been received, proceed to payment.")

        # STEP 1: Generate Access Token
        auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        auth = (settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
        token_response = requests.get(auth_url, auth=auth)

        if token_response.status_code != 200:
            return HttpResponse(f"Failed to get access token: {token_response.text}", status=token_response.status_code)

        try:
            access_token = token_response.json().get('access_token')
        except Exception as e:
            return HttpResponse(f"Error parsing token JSON: {str(e)}", status=500)

        # STEP 2: Generate Password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
        password = base64.b64encode(data_to_encode.encode()).decode()

        # STEP 3: Prepare STK Push Request
        stk_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "NoisePermit",
            "TransactionDesc": "Noise permit payment"
        }

        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        stk_response = requests.post(stk_url, json=payload, headers=stk_headers)

        if stk_response.status_code != 200:
            return HttpResponse(f"STK Push failed: {stk_response.text}", status=stk_response.status_code)

        try:
            result = stk_response.json()
        except Exception as e:
            return HttpResponse(f"Error parsing STK response JSON: {str(e)}", status=500)

        return JsonResponse(result)

    return HttpResponse("Invalid request method", status=400)



