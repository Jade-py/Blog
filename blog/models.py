from django.db import models
from django.urls import reverse
from users.models import customUser
from tinymce.models import HTMLField


class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(customUser, on_delete=models.SET_DEFAULT, default='anonymous')
    body = HTMLField()
    date = models.DateField(auto_now_add=True)
    access_count = models.IntegerField(default=0)
    slug = models.SlugField(max_length=200, unique=True)

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
        return str(self.pk)

# Create your models here.
