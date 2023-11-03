import datetime

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from users.models import customUser
from tinymce.models import HTMLField


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(customUser, on_delete=models.SET_DEFAULT, default='anonymous')
    body = HTMLField()
    date = models.DateField(auto_now_add=True)
    access_count = models.IntegerField(default=0)
    slug = models.SlugField(unique=True, default="")

    def save(self, *args, **kwargs):
        base = slugify(self.title)
        self.slug = base + '-' + str(self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog', args=(self.pk,))


class Comments(models.Model):
    post_pk = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    commenter = models.CharField(max_length=100)
    date_commented = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.pk

# Create your models here.
