from django.test import TestCase, Client
from unittest.mock import patch
import os
from django.contrib.auth import get_user_model
from .models import Post, Comments
from users.models import customUser
from django.urls import reverse
from django.utils.text import slugify


class BlogTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = customUser.objects.create_user(
            username='TestUser',
            password='TestPassword',
            email='test@example.com'
        )

        # Create a test post
        self.post = Post.objects.create(
            title='TestTitle',
            body='A random test text',
            author=self.user,
            slug=slugify('TestTitle')
        )

        # Create a test comment
        self.comment = Comments.objects.create(
            post_pk=self.post,
            comment='A random test comment',
            commenter='TestCommenter'
        )

    def test_post_string_representation(self):
        self.assertEqual(str(self.post), 'TestTitle')

    def test_comment_string_representation(self):
        self.assertEqual(str(self.comment), str(self.comment.pk))

    def test_post_content(self):
        self.assertEqual(self.post.title, 'TestTitle')
        self.assertEqual(self.post.body, 'A random test text')
        self.assertEqual(self.post.author, self.user)

    def test_comment_content(self):
        self.assertEqual(self.comment.comment, 'A random test comment')
        self.assertEqual(self.comment.commenter, 'TestCommenter')
        self.assertEqual(self.comment.post_pk, self.post)

    def test_post_absolute_url(self):
        url = reverse('blog', args=[self.post.pk])
        self.assertEqual(self.post.get_absolute_url(), url)

    def test_post_access_count(self):
        self.assertEqual(self.post.access_count, 0)


class BlogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(
            title='Test Post',
            body='This is a test post content',
            author=self.user,
            slug=slugify('Test Post')
        )

    def test_all_blogs_view(self):
        response = self.client.get(reverse('blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AllBlogs.html')
        self.assertContains(response, 'Test Post')

    def test_blog_post_view(self):
        response = self.client.get(reverse('blog', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog.html')
        self.assertContains(response, 'Test Post')

        # Test access count increment
        self.post.refresh_from_db()
        self.assertEqual(self.post.access_count, 1)

    def test_blog_post_comment(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('blog', kwargs={'slug': self.post.slug}), {
            'comment': 'This is a test comment'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after comment
        self.assertTrue(Comments.objects.filter(post_pk=self.post, comment='This is a test comment').exists())

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Test Post')

    def test_delete_blog_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('delete', kwargs={
            'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Post.objects.filter(slug=self.post.slug).exists())

    def test_dashboard_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_dashboard.html')

        # Test creating a new post
        response = self.client.post(reverse('user'), {
            'title': 'New Test Post',
            'body': 'This is a new test post content'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(title='New Test Post').exists())

    def test_unauthenticated_access(self):
        response = self.client.get(reverse('user'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_comment_redirect_for_unauthenticated_user(self):
        response = self.client.post(reverse('blog', kwargs={'slug': self.post.slug}), {
            'comment': 'This comment should not be saved'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertFalse(Comments.objects.filter(comment='This comment should not be saved').exists())

    @patch('smtplib.SMTP')
    def test_mail_sent_on_comment(self, mock_smtp):
        # Set up the mock
        mock_server = mock_smtp.return_value.__enter__.return_value

        # Log in the user
        self.client.login(username='testuser', password='12345')

        # Create a post by another user
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='12345',
            email='otheruser@example.com'
        )
        post = Post.objects.create(
            title='Other User Post',
            body='This is a post by another user',
            author=other_user,
            slug=slugify('Other User Post')
        )

        # Post a comment
        response = self.client.post(reverse('blog', kwargs={'slug': post.slug}), {
            'comment': 'This is a test comment'
        })

        # Check that the comment was saved
        self.assertTrue(Comments.objects.filter(post_pk=post, comment='This is a test comment').exists())

        # Check that an email was "sent"
        self.assertTrue(mock_server.send_message.called)

        # Print email details for debugging
        call_args = mock_server.send_message.call_args
        email_msg = call_args[0][0]
        print("From:", email_msg['From'])
        print("To:", email_msg['To'])
        print("Subject:", email_msg['Subject'])
        print("Body:", email_msg.get_payload())

        # Assertions
        self.assertEqual(email_msg['From'], os.environ.get('DEFAULT_FROM_EMAIL'))
        self.assertEqual(email_msg['To'], 'otheruser@example.com')
        self.assertIn('New comment on your blog post!', email_msg.get_payload())
        self.assertIn('Other User Post', email_msg.get_payload())

        # Check the response
        self.assertEqual(response.status_code, 302)  # Redirect after comment