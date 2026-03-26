from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('shop attendant', 'Shop Attendant'),
        ('supervisor', 'Supervisor'),
        ('weighter', 'Weighter'),
        ('chef', 'Chef'),
    ]

    LOCATION_CHOICES = [
        ('kisumu', 'Kisumu'),
        ('kamamega', 'Kamamega'),
        ('all', 'All')
    ]


    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(
        max_length=20,
        choices=[('bar', 'Bar'), ('kitchen', 'Kitchen'), ('rooms', 'Rooms'),('all','All')],
        blank=True,
        null=True
    )
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.username