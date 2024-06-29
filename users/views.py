from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils import timezone
from .models import Review
from .forms import ReviewForm
import requests
from django.contrib import messages


@login_required
def home(request):
    search_query = request.GET.get('search')
    search_by = request.GET.get('search_by')
    breweries = []

    if search_query:
        if search_by == 'city':
            response = requests.get(f"https://api.openbrewerydb.org/breweries?by_city={search_query}")
        elif search_by == 'name':
            response = requests.get(f"https://api.openbrewerydb.org/breweries?by_name={search_query}")
        elif search_by == 'type':
            response = requests.get(f"https://api.openbrewerydb.org/breweries?by_type={search_query}")
    else:
        response = requests.get("https://api.openbrewerydb.org/breweries")

    if response.status_code == 200:
        breweries = response.json()
        for brewery in breweries:
            average_rating = Review.objects.filter(brewery_id=brewery['id']).aggregate(Avg('rating'))['rating__avg']
            brewery['average_rating'] = average_rating if average_rating is not None else 'No ratings yet'
    else:
        error_message = "API request failed. Please try again later."
        return render(request, 'home.html', {'error_message': error_message})

    return render(request, 'home.html', {'breweries': breweries})

@login_required
def brewery_details(request, brewery_id):
    try:
        response = requests.get(f"https://api.openbrewerydb.org/breweries/{brewery_id}")
        response.raise_for_status()  # Raise an error for bad responses
        brewery = response.json()

        # Fetch reviews for the brewery from the database
        reviews = Review.objects.filter(brewery_id=brewery_id)

        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.brewery_id = brewery_id  # Save brewery_id as a foreign key
                review.created_at = timezone.now() 
                review.save()
                messages.success(request, 'Review added successfully!')
                return redirect('brewery_details', brewery_id=brewery_id)
        else:
            form = ReviewForm()

        return render(request, 'brewery_details.html', {'brewery': brewery, 'reviews': reviews, 'form': form})

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Error connecting to API: {str(e)}')
        return HttpResponse("Error connecting to Brewery API.", status=500)
    except Exception as e:
        messages.error(request, f'Something went wrong: {str(e)}')
        return HttpResponse("Error processing request.", status=500)

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Your passwords do not match!")
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('login')

    return render(request, 'signup.html')

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Username or Password is incorrect!")

    return render(request, 'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')