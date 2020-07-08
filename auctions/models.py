from django.contrib.auth.models import AbstractUser
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
