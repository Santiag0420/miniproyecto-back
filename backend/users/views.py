from django.shortcuts import render
from django.http import JsonResponse
from .models import Usuario

def listar_users(request):
    users = Usuario.objects.all().values('id','created_at', 'name', 'age')
    return JsonResponse(list(users), safe=False)

