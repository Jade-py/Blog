from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.urls import reverse_lazy
from django.views.generic import *
from .models import customUser


class signupView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'Signup.html'


def username_taken(request):
    queryset = customUser.objrctd.all()
    for user in queryset:
        if request.POST.username == user:
            return render()


class editUserView(UpdateView):
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('user')
    template_name = 'edit_user.html'

    def get_object(self, queryset=None):
        return self.request.user

# Create your views here.
