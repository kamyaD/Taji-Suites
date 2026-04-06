from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect

def auto_logout(request):
    logout(request)
    return redirect('login')

# Create your views here.
