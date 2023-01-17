from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *


def index(request):
    auctionListings = AuctionItem.objects.all()
    return render(request, "auctions/index.html", {
        "auctionListings": auctionListings
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


@login_required(login_url='login')
def new_listing(request):
    if request.method == "POST":
        form = AuctionItemForm(request.POST)
        if form.is_valid():
            newItem = AuctionItem()
            newItem.title = form.cleaned_data["title"]
            newItem.description = form.cleaned_data["description"]
            newItem.image_url = form.cleaned_data["image_url"]
            newItem.starting_bid = form.cleaned_data["starting_bid"]
            newItem.category = form.cleaned_data["category"]           
            newItem.author = request.user
            newItem.save()
            return HttpResponseRedirect(reverse("index"))

    form = AuctionItemForm()
    return render(request, "auctions/new_listing.html", {
        "form": form
    })


def current_listing(request, id):
    listing = AuctionItem.objects.get(pk=id)
    add_to_wl = False
    comment_form = CommentForm()
    comments = Comment.objects.all()
    bid_form = BidForm()
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        if request.POST["button"] == "watchlist":
            if not user.watchlist.filter(item=listing):
                wl = Watchlist()
                wl.item = listing
                wl.user = user
                wl.save()
            else:
                user.watchlist.filter(item=listing).delete()
            
            return HttpResponseRedirect(reverse('current_listing', args=(id,)))

    user = request.user

    # if request.user.username == listing.winner:
    #         messages.success(request, "Congratulations! Your bid as won this listing!")
    #         return HttpResponseRedirect(reverse("current_listing", args=(id,)))

    
    if listing.winner == user.username and listing.isClosed == True:
        return render(request, "auctions/current_listing.html", {
        "item": listing,
        "comment_form": comment_form,
        "comments": listing.comment_item.all(),
        "bid_form": bid_form,
        "message_success": "Congratulations! Your bid as won this listing!"
    })
    elif listing.author == user:
        return render(request, "auctions/current_listing.html", {
        "item": listing,
        "comment_form": comment_form,
        "comments": listing.comment_item.all(),
        "bid_form": bid_form,
        "creator": True
    })
    else:
        return render(request, "auctions/current_listing.html", {
        "item": listing,
        "comment_form": comment_form,
        "comments": listing.comment_item.all(),
        "bid_form": bid_form
    })


def watchlist(request):
    user = request.user
    return render(request, "auctions/watchlist.html", {
        "wl": user.watchlist.all()
    })

@login_required(login_url='login')
def comment(request, id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=request.user)
            item = AuctionItem.objects.get(pk=id)
            text = form.cleaned_data["text"]
            comment = Comment()
            comment.user = user
            comment.item = item
            comment.text = text
            comment.save()
            return HttpResponseRedirect(reverse('current_listing', args=(id,)))


def category(request):
    return render(request, "auctions/categories.html", {
    "categories": dict(CATEGORY_CHOICES)
    })


def category_items(request, category_name):
    items = AuctionItem.objects.filter(category=category_name)
    return render(request, "auctions/category_items.html", {
        "items": items
    })


def bid(request, id):
    item = AuctionItem.objects.get(pk=id)
    if not item.isClosed:
        author = item.author
        bid = Bid()
        bid.user = request.user
        if request.method == "POST":
            form = BidForm(request.POST)
            if form.is_valid():
                bid.price = form.cleaned_data["bid"]
                if bid.user != author:
                    if bid.price >= item.starting_bid:
                        item.starting_bid = bid.price
                        item.winner = bid.user.username
                        item.save()
                        return HttpResponseRedirect(reverse("current_listing", args=(id,)))
                    else:
                        messages.error(request, "Insufficient bid!")
                        return HttpResponseRedirect(reverse("current_listing", args=(id,)))
                else:
                    messages.error(request, "You cannot bid on your own item!")
                    return HttpResponseRedirect(reverse("current_listing", args=(id,)))
    else:
        messages.error(request, "This listing is closed!")
        return HttpResponseRedirect(reverse("current_listing", args=(id,)))




def close(request, id):
    if request.method == "POST":
        if request.POST["closed"] == "true":
            item = AuctionItem.objects.get(pk=id)
            item.isClosed = True
            item.save()
            return HttpResponseRedirect(reverse('current_listing', args=(id,)))
            















CATEGORY_CHOICES = (
    ("Home", "Home"),
    ("Electronics", "Electronics"),
    ("Sports", "Sports"),
    ("Fashion", "Fashion"),
    ("Travel", "Travel"),
    ("None", "None")
)
class AuctionItemForm(forms.Form):
    title = forms.CharField(max_length=64)
    description = forms.CharField(widget=forms.Textarea)
    image_url = forms.CharField(max_length=256, required=False)
    starting_bid = forms.IntegerField()
    category = forms.ChoiceField(choices=CATEGORY_CHOICES)


class CommentForm(forms.Form):
    text = forms.CharField(label="Comment:", widget=forms.Textarea)

class BidForm(forms.Form):
    bid = forms.IntegerField(label="Bid:")
