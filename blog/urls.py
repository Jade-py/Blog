from django.urls import path
from .views import *

urlpatterns = [
    path('', homeView.as_view(), name='home'),
    path('blogs/', AllBlogsView.as_view(), name='blogs'),
    path('post/<slug:slug>/', blog_post.as_view(), name='blog'),
    path('post/<slug:slug>/delete/', deleteBlogView.as_view(), name='delete'),
    path('user/', dashboard_view, name='user'),
]
