from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Comment


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'category']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request):
    if request.method == 'POST':
        listing = ListingForm(request.POST)
        listing.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/listing.html",{
            'form': ListingForm()
        })

def listing_page(request, page_id):
    page = Listing.objects.get(id=page_id)
    return render(request, "auctions/listing_page.html", {
        'listing':page,
        'comments':page.comments.all(),
        'form': CommentForm()
    })

def create_comment(request, page_id):
    if request.method == 'POST':
        page = Listing.objects.get(id=page_id)
        print('get page')
        comment = CommentForm(request.POST)
        new_comment = comment.save(commit=False)
        #new_comment.listing.add(page)
        page.comments.add(new_comment,bulk=False)
        new_comment.save()
        return HttpResponseRedirect(reverse('listing_page', args=(page.id,)))

def category(request):
    return render(request, "auctions/category.html", {
        "categories": Listing.CATEGORIES
    })

def category_view(request, category):
    listings = Listing.objects.filter(category=category).all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })