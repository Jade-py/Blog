from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class customUser(AbstractUser):
    username = models.CharField(max_length=50, primary_key=True, unique=True)
    email = models.EmailField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('user', args=(self.pk,))


# Create your models here.
