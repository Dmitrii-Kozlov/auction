from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import ModelForm, TextInput, Textarea, NumberInput
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Comment, Bid


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['image','title', 'description', 'category']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control'}),
            'image': TextInput(attrs={'class': 'form-control'})
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={'class': 'form-control'})
        }

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']
        widgets = {
            'bid': NumberInput(attrs={'class': 'form-control'})
        }



def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
        'title': 'Active Listings'
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

@login_required
def listing(request):
    if request.method == 'POST':
        listing = ListingForm(request.POST)
        bid = BidForm(request.POST)
        if listing.is_valid() and bid.is_valid():
            new_listing = listing.save(commit=False)
            new_listing.owner = request.user
            new_listing = listing.save()
            new_bid = bid.save(commit=False)
            new_bid.user = request.user
            new_bid.listing = new_listing
            new_bid.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "auctions/listing.html", {
                'listing_form': listing,
                'bid_form': bid
            })
    else:
        return render(request, "auctions/listing.html",{
            'listing_form': ListingForm(),
            'bid_form': BidForm()
        })

def listing_page(request, page_id):
    page = Listing.objects.get(id=page_id)
    try:
        remove = page in request.user.listings.all()
    except:
        remove = False
    close_auction = page.active and request.user == page.owner
    bid = page.bids.order_by('bid').last()
    return render(request, "auctions/listing_page.html", {
        'listing':page,
        'comments':page.comments.all(),
        'comment_form': CommentForm(),
        'bid_form': BidForm(),
        'bid': bid,
        'remove': remove,
        'close_auction':close_auction,
        'active':page.active
    })

@login_required
def create_comment(request, page_id):
    if request.method == 'POST':
        page = Listing.objects.get(id=page_id)
        comment = CommentForm(request.POST)
        new_comment = comment.save(commit=False)
        new_comment.user = request.user
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
        "listings": listings,
        'title': [x[1] for x in Listing.CATEGORIES if x[0] == category][0]
    })

@login_required
def watchlist(request):
    if request.method == 'POST':
        try:
            id = request.POST['add_to_watchlist']
            request.user.listings.add(id)
        except:
            id = request.POST['remove_from_watchlist']
            request.user.listings.remove(id)
        return HttpResponseRedirect(reverse('listing_page', args=(id,)))
    user_list = request.user.listings.all()
    return render(request, "auctions/index.html", {
        "listings": user_list,
        'title': 'Watchlist'
    })

@login_required
def place_bid(request, page_id):
    if request.method == 'POST':
        page = Listing.objects.get(id=page_id)
        bid = BidForm(request.POST)
        if bid.is_valid():
            new_bid = bid.save(commit=False)
            new_bid.user = request.user
            new_bid.listing = page
            request.user.bids.add(new_bid, bulk=False)
            page.bids.add(new_bid,bulk=False)
            new_bid.save()
        return HttpResponseRedirect(reverse('listing_page', args=(page.id,)))

@login_required
def close_auction(request):
    if request.method == 'POST':
        id = request.POST['close_auction']
        page = Listing.objects.get(id=id)
        page.active = False
        page.save()
        return HttpResponseRedirect(reverse('index'))