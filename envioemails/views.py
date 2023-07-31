import datetime
import json
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView
from empbase.models import Empresa, Escritorio
from empbase.views import getUA

'''import requests

# Step 1: Send a GET request to obtain the CSRF token
response = requests.get('http://127.0.0.1:8000/envioemails?id=2747')
csrftoken = response.cookies.get('csrftoken')
'''

@method_decorator(csrf_exempt, name='dispatch')
class Envioemails(TemplateView):

    def get(self, request, **kwargs):
        if 'cnpj' in request.GET:
            emp = Empresa.objects.get(cnpj=request.GET['cnpj'])
            empjson = {
                'cod': emp.cod,
                'nome': emp.nome,
                'cnpj': emp.cnpj,
                'forma': emp.formaenvio,
                'email': emp.email,
                'cidade': emp.municipio,
                'uf': emp.uf
            }
            return JsonResponse({'emp': empjson})
        return JsonResponse({'msg':'sucesso'})
    

    def post(self, request, **kwargs):
        rpost = request.POST
        if 'username' in rpost:
            user = authenticate(request, username=rpost['username'], password=rpost['password'])
            if user is not None:
                login(request, user)
                return JsonResponse({'msg':'logado'})
            else:
                return JsonResponse({'msg':'Usuario e ou senha incorretos'})
        if 'cnpj' in rpost:
            ua, acesso = getUA(request.user)
            emp = request.user.temacesso.emp.get(cnpj=rpost['cnpj'])
            valorpost = float(rpost['valor'].replace(',', '.'))
            comppost = datetime.datetime.strptime(rpost['comp'], "%Y-%m-%d %H:%M:%S")
            vctopost = datetime.datetime.strptime(rpost['vcto'], "%Y-%m-%d %H:%M:%S")
            
            imposto = emp.imposto_set.filter(nome=rpost['imposto'], comp__year=comppost.year, comp__month=comppost.month)
            imposto = imposto[0] if imposto else None
            if imposto:
                if imposto.nome == 'INSS':
                    ir = emp.imposto_set.filter(nome='IR', comp=comppost)
                    if ir:
                        imposto.valor += ir[0].valor
                if abs(imposto.valor - valorpost) <= 1.5:
                    if imposto.enviado:
                        return JsonResponse({'msg':'enviado'})
                    return JsonResponse({'msg':'enviar', 'id': imposto.id})
                else:
                    return JsonResponse({'msg':'valor diferente'})
            else:
                imp = emp.imposto_set.create(nome=rpost['imposto'], valor=valorpost, comp=comppost, vcto=vctopost)
                return JsonResponse({'msg':'enviar', 'id': imp.id})
        if 'confirma' in rpost:
            imposto.enviado = True
            imposto.save()
            return JsonResponse({'msg':'enviado'})
        

'''import requests

data = {
    'usuario': 'Guilherme',
    'senha': 'uiui'
}

# Step 1: Obtain the CSRF token
response = requests.get('http://127.0.0.1:8000/envioemails')
csrftoken = response.cookies['csrftoken']

# Step 2: Include the CSRF token in the headers of your API requests
headers = {'X-CSRFToken': csrftoken}

# Step 3: Send your API request with the CSRF token in the headers
response = requests.post('http://127.0.0.1:8000/envioemails', headers=headers, json=data)
print(response.json())'''
