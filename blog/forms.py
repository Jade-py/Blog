from django import forms
from .models import Post, Comments
from tinymce.widgets import TinyMCE


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body',)
        widgets = {'body': TinyMCE()}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('comment',)
