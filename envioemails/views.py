import datetime
import json
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView
from requests import Response
from ecpsite import settings
from empbase.models import Empresa, Escritorio, UltimoAcesso
from empbase.views import getUA
from envioemails.processapdf import processa_guia


@csrf_exempt  # Disable CSRF protection for this view
def login_api(request):
    print(request.POST)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = JsonResponse({'message': 'Login successful', 'sessionid': request.session.session_key}, status=200)
            return response
        else:
            return JsonResponse({'message': 'Invalid username or password'}, status=401)
    else:
        # Handle unsupported HTTP methods
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@csrf_exempt
def envioguias(request):
    if request.method == 'POST':
        print(request.POST, request.FILES)
        user = request.user
        ua = UltimoAcesso.objects.filter(user=user).first()
        acesso = user.temacesso.emp.filter(escr=ua.escr)
        emp = processa_guia(request.FILES['file'], user)
        return JsonResponse({'msg':emp.nome})


'''        
import requests

def acessa():
    # Define the API endpoint for login
    url = 'http://127.0.0.1:8000/login_api'
    # Define the login credentials
    login_data = {
        'username': 'Guilherme',
        'password': 'uiui'
    }
    # Make a POST request to the login endpoint with the login data
    response = requests.post(url, data=login_data)
    # Check the response status code
    if response.status_code == 200:
        print("Login successful!")
        sessionid = response.json().get('sessionid')
        return sessionid
        # You can access response data like response.json() if the API returns JSON data
    else:
        print("Login failed. Status code:", response.status_code)


def consulta(file, sessionid):
        url = 'http://127.0.0.1:8000/envioguias'
        headers = {'Cookie': f'sessionid={sessionid}'}
        with open(file, 'rb') as file:
            print(file)
            response = requests.post(url, headers=headers, files={'file': file})
        print(response.json())
'''
