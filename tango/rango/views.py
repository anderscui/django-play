from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm

def index(request):
    categories = Category.objects.order_by('-likes')[:5]
    cxt = { 'categories': categories }
    return render(request, 'rango/index.html', cxt)

def category(request, name_slug):
    cxt = {}

    try:
        c = Category.objects.get(slug=name_slug)
        cxt['category_name'] = c.name

        pages = Page.objects.filter(category=c)
        cxt['pages'] = pages
        cxt['category'] = c
    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', cxt)

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form': form})
