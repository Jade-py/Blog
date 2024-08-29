from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import *
from .models import Post, Comments
from .forms import PostForm, CommentForm
import datetime
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from environs import Env

env = Env()
env.read_env()

# Define the sender's and receiver's email addresses
sender_email = os.environ.get('DEFAULT_FROM_EMAIL')
email_host = os.environ.get('EMAIL_HOST')
email_host_user = os.environ.get('EMAIL_HOST_USER')
email_host_password = os.environ.get('EMAIL_HOST_PASSWORD')
email_port = int(os.environ.get('EMAIL_PORT', 587))
email_use_tls = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'

subject = 'New comment on your blog post!'

# A custom mixin to check whether request is from an authenticated user
def login_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return redirect('login')

    return wrapper


# Lists all the blogs
class AllBlogsView(ListView):
    model = Post
    template_name = 'AllBlogs.html'
    context_object_name = 'all_blogs_list'

    def get_queryset(self):
        return Post.objects.order_by("-access_count")


# Lists each of the requested post
class blog_post(DetailView):
    model = Post
    form_class = CommentForm
    success_url = reverse_lazy('blog')
    template_name = 'blog.html'

    # Returns all the comments related to the post in a context variable
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        comments = Comments.objects.filter(post_pk=post)
        context['comments'] = comments
        return context

    # Gets the access count (How many times the post has been clicked) and increments it by 1
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.access_count += 1
        self.object.save()
        return super().get(self, request, *args, **kwargs)

    # Processes and saves the comment
    def post(self, request, slug):
        pk = self.get_object().slug
        print(pk)
        if request.user.is_authenticated:
            if request.method == 'POST':
                comment = request.POST.get('comment')
                post = get_object_or_404(Post, slug=slug)
                comment = Comments(
                    post_pk=post,
                    comment=comment,
                    commenter=request.user,
                    date_commented=datetime.date.today()
                )
                comment.save()

                body = f"Dear {post.author.username},\n\nSomeone has commented on your blog post titled '{post.title}'.\n\nYou can reply to this comment or view the post by clicking here: {self.request.build_absolute_uri(reverse('blog', kwargs={'slug': post.slug}))}\n\nBest regards,\nThe Phantasmagoria"
                receiver_email = post.author.email
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = subject
                message.attach(MIMEText(body, "plain"))

                try:
                    with smtplib.SMTP(email_host, email_port) as server:
                        if email_use_tls:
                            server.starttls()
                        server.login(email_host_user, email_host_password)
                        server.send_message(message)
                    print("Email sent successfully!")
                except Exception as e:
                    print(f"An error occurred: {e}")

            else:
                pass
        else:
            # If not authenticated while trying to comment,
            # User is sent to login page and then to the post the user was on
            login_url = reverse('login') + f'?next={reverse("blog", args=[pk])}'
            return redirect(login_url)
        return redirect('blog', slug=slug)


# The landing page
class homeView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'all_blogs_list'

    # Gets all posts sorted based on access count
    def get_queryset(self):
        return Post.objects.order_by("-access_count")


# Delete a post
class deleteBlogView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('user')

    # This avoids the confirmation and deletes the post directly on click
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())


# New posts can be created and all the previous ones are listed alongside on the same page
@login_required
def dashboard_view(request):
    blog_list = Post.objects.filter(author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post(
                title=form.cleaned_data['title'],
                body=form.cleaned_data['body'],
                author=request.user,
                slug=slugify(form.cleaned_data['title'])
            )
            post.save()
        else:
            print(form.errors)
    else:
        form = PostForm()
    return render(request, 'user_dashboard.html', {'form': form, 'blog_list': blog_list})
