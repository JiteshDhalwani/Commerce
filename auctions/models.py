from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField()
    def __str__(self):
        return f"Bid made by {self.user} | Price: {self.price}"


CATEGORY_CHOICES = (
    ("Home", "Home"),
    ("Electronics", "Electronics"),
    ("Sports", "Sports"),
    ("Fashion", "Fashion"),
    ("Travel", "Travel"),
    ("None", "None")
)
class AuctionItem(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image_url = models.CharField(max_length=256, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    starting_bid = models.IntegerField()
    isClosed = models.BooleanField(default=False)
    winner = models.CharField(max_length=30, null=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="None"
    )
    def __str__(self):
        return f"{self.id}: {self.title} created by {self.author}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, blank=True, related_name="wl_item")

    def __str__(self):
        return f"{self.user}'s watchlist"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name="comment_item")
    text = models.TextField()

    def __str__(self):
        return f"{self.id}: Comment made by {self.user} on {self.item}"
