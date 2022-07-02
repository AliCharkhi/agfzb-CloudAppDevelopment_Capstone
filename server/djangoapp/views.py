from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def index(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/index.html', context)

# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            messages.error(request, 'Username or password is incorrect')
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)


# Create a `logout_request` view to handle sign out request
# def logout_request(request):
def logout_request(request):
    context = {}
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
# def registration_request(request):
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(
                username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://704f8f89.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(
        request,
        dealer_id,
        url="https://704f8f89.us-south.apigw.appdomain.cloud/api/"):
    if request.method == "GET":
        context = {
            "dealer": get_dealer_by_id_from_cf(url + 'dealership', dealer_id),
            "reviews": get_dealer_reviews_from_cf(url + 'review', dealer_id)}
        #return render(request, 'djangoapp/dealer_details.html', context)
        return HttpResponse(context["reviews"])
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(
    request,
    dealer_id,
    url = "https://704f8f89.us-south.apigw.appdomain.cloud/api/"):    
    if request.method == "GET":
        get_url = url + "dealership"
        dealer = get_dealer_by_id_from_cf(get_url, dealer_id)
        cars = CarModel.objects.all()
        context = {
            "cars": cars,
            "dealer": dealer,
        }
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST":
        if request.user.is_authenticated:
            post_url = url + "review"
            post_res = request.POST
            car_id = post_res["car"]
            car = CarModel.objects.get(pk=car_id)
            review = dict()
            review["name"] = request.user.username
            review["dealership"] = dealer_id
            review["id"] = random.randint(1, 100)
            review["review"] = post_res["content"]
            if post_res["purchasecheck"] == 'on':
                review["purchase"] = True
                review["purchase_date"] = post_res["purchasedate"]
            else:
                review["purchase"] = False
                review["purchase_date"] = None
            review["car_make"] = car.car_make.name
            review["car_model"] = car.name
            review["car_year"] = int(car.year.strftime("%Y"))
            json_payload = {"review": review}
            post_request(post_url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
