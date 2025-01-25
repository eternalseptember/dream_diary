from django.shortcuts import render
from django.http import HttpResponse


def dreams_index(request):
    return HttpResponse("Hello, Django!")
