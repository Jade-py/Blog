from django.test import TestCase
from .models import *
from django.urls import reverse

class setup(TestCase):
    def BlogTests(self):
        self.post = Post.objects.creeate(title='TestTitle', body='A random test text', author=self.user)

    def test_string_representation(self):
        post = Post.title
        self.assertEqual(str(post), post.title)

    def 
# Create your tests here.
