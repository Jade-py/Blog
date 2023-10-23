from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', homeView.as_view(), name='home'),
    path('blogs/', AllBlogsView.as_view(), name='blogs'),
    path('contact/', contactView, name='contact'),
    path('post/<int:pk>/', blog_post.as_view(), name='blog'),
    path('post/new/', newBlogView.as_view(), name='newBlog'),
    path('post/<int:pk>/edit/', updateBlogView.as_view(), name='editBlog'),
    path('post/<int:pk>/delete/', deleteBlogView.as_view(), name='delete'),
    path('user/', dashboard_view, name='user'),
    path('myBlog/', userBlogView.as_view(), name='userPosts'),

]
