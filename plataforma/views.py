from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import time

def index(request):
    return HttpResponse("O app plataforma está funcionando!")

