from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    CategoryName = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.CategoryName}"
    

class Bid(models.Model):
    bid = models.IntegerField(default=0)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, null="True", blank="True", related_name="bidder")

    def __str__(self):
        return f"{self.bid} by {self.bidder}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length = 1000)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")
    imageURL = models.CharField(max_length=1000)
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist=models.ManyToManyField(User, blank=True, null=True, related_name="listingWatchlist")

    def __str__(self):
        return f"{self.title} by {self.owner}"




class Comment(models.Model):
    comment = models.CharField(max_length=255)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, null="True", blank="True", related_name="commenter")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null="True", blank="True", related_name="listing")

    def __str__(self):
        return f"{self.comment} by {self.commenter}"
