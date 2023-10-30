import datetime
from django import template
import hashlib

register = template.Library()

@register.filter
def hash_id(id):
    # Convert the ID to a string
    id_string = str(id)
    # Create a hashlib object using the SHA256 algorithm
    hash_object = hashlib.sha256(id_string.encode())
    # Get the hexadecimal representation of the hash
    hash_value = hash_object.hexdigest()
    # Return the hash value
    return hash_value

@register.filter
def calcula_minuto(value):
    modulo = 60 * (value % 1)
    if modulo == 0:
        value = str(int(value))
        hora = value if len(value) == 2 else '0' + value
        return f'{hora}:00'
    else:
        hora = str(int(value))
        hora = hora if len(hora) == 2 else '0' + hora
        minuto = str(int(modulo))
        minuto = minuto if len(minuto) == 2 else '0' + minuto
        return f'{hora}:{minuto}'
    
@register.filter
def ajusta_hora(time):
    hora = time.hour
    minuto = time.minute
    if hora == 0:
        hora = "00"
    if minuto == 0:
        minuto = "00"
    if len(str(hora)) == 1:
        hora = "0" + str(hora)
    if len(str(minuto)) == 1:
        minuto = "0" + str(minuto)

    fullhora = f'{hora}:{minuto}'
    return fullhora

@register.filter()
def date_format(value, format_string):
    if isinstance(value, datetime):
        return value.strftime(format_string)
    return value

@register.filter()
def makerange(val, max):
    total = []
    for i in range(val, max):
        i = str(i)
        total.append(i if len(i) >= 2 else '0' + i)
    return total

@register.filter()
def faltas(obj):
    falta = obj.filter(rub__name='Horas Faltas')
    if falta:
        return falta[0].valor
    return falta


@register.filter()
def alocacoes(aloc, ua):
    aloc = aloc.filter(comp__month=ua.comp.month, comp__year=ua.comp.year)
    return aloc

@register.filter()
def soma_lancamentos(lancamentos, ua):
    lancamentos = lancamentos.filter(comp__year=ua.comp.year, comp__month=ua.comp.month).order_by('comp')
    somavalores = {}
    for lancamento in lancamentos:
        nome = f'{lancamento.rub.cod} - {lancamento.rub.name}'
        valor = lancamento.valor
        if nome in somavalores:
            somavalores[nome] += valor
        else:
            somavalores[nome] = valor
    print(somavalores)
    return somavalores
    