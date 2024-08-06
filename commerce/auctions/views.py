from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *


def index(request):
    return render(request, "auctions/index.html", {
        "activeListings" : Listing.objects.filter(isActive=True),
        "categories": Category.objects.all()
    })




def filterCategory(request):
    if request.method == "POST":
        selectedCategory = request.POST["category"]
        category = Category.objects.get(CategoryName = selectedCategory)
        activeListings = Listing.objects.filter(isActive=True, category = category)

        return render(request, "auctions/index.html", {
            "activeListings" : activeListings,
            "categories": Category.objects.all()
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


def create(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories" : categories
        })
    
    else:
        curentUser = request.user
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        url = request.POST["url"]
        category = request.POST["category"]

        category1 = Category.objects.get(CategoryName = category)

        bid = Bid(bid=float(price), bidder = curentUser)
        bid.save()

        newListing = Listing(
            title= title,
            description =  description,
            price= bid,
            imageURL= url,
            category= category1,
            owner = curentUser
        )

        newListing.save()

        return HttpResponseRedirect(reverse(index))

def listing(request, id):
    this_listing = Listing.objects.get(pk=id )
    isListinginWatchlist = request.user in this_listing.watchlist.all()
    allComments = Comment.objects.filter(listing=this_listing)
    isOwner = request.user.username == this_listing.owner.username
    return render(request, "auctions/listing.html", {
        "listing" : this_listing,
        "isListinginWatchlist" : isListinginWatchlist,
        "comments": allComments,
        "isOwner": isOwner

    })

def addBid(request, id):
    newBid = request.POST["newBid"]
    listingData = Listing.objects.get(pk=id)
    isListinginWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    if int(newBid) > listingData.price.bid:
        updateBid = Bid(bidder=request.user , bid = int(newBid))
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message" : "Bid Successful",
            "update": True,
            "isListinginWatchlist" : isListinginWatchlist,
            "comments": allComments,
            "isOwner" : isOwner,
        })
    
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message" : "Bid Failed",
            "update": False,
            "isListinginWatchlist" : isListinginWatchlist,
            "comments": allComments,
            "isOwner" : isOwner,
        })


def closeAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    isListinginWatchlist = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username 
    listingData.save()
    return render(request, "auctions/listing.html",{
        "listing" : listingData,
        "isListinginWatchlist" : isListinginWatchlist,
        "comments": allComments,
        "isOwner": isOwner,
        "update" : True,
        "message": "Congrats, your auction is closed"
    })



def removeFromWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addToWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def watchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings" : listings
    })

def addComment(request, id):
    currentUser=request.user
    listingData=Listing.objects.get(pk=id)
    message = request.POST["newComment"]

    newComment=Comment(
        commenter = currentUser,
        listing = listingData,
        comment = message
    )

    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=(id, )))
    