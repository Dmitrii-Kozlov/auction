from django.contrib.auth.models import AbstractUser
from django.core.validators import DecimalValidator
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    CATEGORIES = [
        ('H', 'Home'),
        ('F', 'Fashion'),
        ('T', 'Toys'),
        ('E', 'Electronics'),
        ('O', 'Other')
    ]
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.CharField(max_length=1, choices=CATEGORIES)
    watching = models.ManyToManyField(User,related_name='listings')

class Comment(models.Model):
    text = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f'{self.text}'

class Bid(models.Model):
    bid = models.DecimalField(max_digits=11, decimal_places=2, validators=[DecimalValidator(max_digits=11, decimal_places=2)])
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')