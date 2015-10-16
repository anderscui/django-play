from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


def index(request):

    cat_list = Category.objects.order_by('-likes')[:10]
    page_list = Page.objects.order_by('-views')[:10]
    cxt_dict = {'categories': cat_list, 'pages': page_list}

    visits = int(request.COOKIES.get('visits', 1))

    reset_last_visit_time = False
    resoponse = render(request, 'rango/index.html', cxt_dict)

    if 'last_visit' in request.COOKIES:
        last_visit = request.COOKIES['last_visit']
        last_visit_time = datetime.strptime(last_visit[:-7], '%Y-%m-%d %H:%M:%S')

        # TODO: update this
        if (datetime.now() - last_visit_time).seconds > 10:
            visits += 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True
        cxt_dict['visits'] = visits
        resoponse = render(request, 'rango/index.html', cxt_dict)

    if reset_last_visit_time:
        resoponse.set_cookie('last_visit', datetime.now())
        resoponse.set_cookie('visits', visits)

    return resoponse


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

@login_required
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

@login_required
def add_page(request, cat_name_slug):

    try:
        cat = Category.objects.get(slug=cat_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():

            if form.is_valid():
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()

                return category(request, cat_name_slug)

        else:
            print form.errors
    else:
        form = PageForm()

    return render(request, 'rango/add_page.html', {'form': form, 'category': cat})


## auth views
def register(request):

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )


def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return HttpResponse('Since you are logged in, you cna see this text!')


@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')


def about(request):
    return render(request, 'rango/about.html')
