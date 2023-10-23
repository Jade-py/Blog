from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from.models import customUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = customUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')


class CustomUserChangeForm(forms.ModelForm):
    class Meta(UserChangeForm):
        model = customUser
        fields = ('first_name', 'last_name', 'email')