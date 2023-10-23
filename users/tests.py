from django.test import TestCase
from django.contrib.auth import get_user_model

class BlogTests(TestCase):

    def setup(self):
        self.user = get_user_model().objects.create_user(username='testuser', first_name='test', last_name='user',email='tet@user.com', password='test123')

        self.post = Post.objects.create()


# Create your tests here.
