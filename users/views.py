from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm


# Create your views here.

def login(request):
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
