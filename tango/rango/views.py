from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category

def index(request):
    categories = Category.objects.order_by('-likes')[:5]
    cxt = { 'categories': categories }
    return render(request, 'rango/index.html', cxt)

