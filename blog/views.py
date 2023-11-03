from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import *
from .models import Post, Comments
from .forms import PostForm, CommentForm
import datetime


def login_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper


class AllBlogsView(ListView):
    model = Post
    template_name = 'AllBlogs.html'
    context_object_name = 'all_blogs_list'

    def get_queryset(self):
        return Post.objects.order_by("-access_count")


def contactView(request):
    return render(request, 'contact.html')


class blog_post(DetailView):
    model = Post
    form_class = CommentForm
    success_url = reverse_lazy('blog')
    template_name = 'blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        comments = Comments.objects.filter(post_pk=post)
        context['comments'] = comments
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.access_count +=1
        self.object.save()
        return super().get(self, request, *args, **kwargs)

    def post(self, request, pk):
        if request.user.is_authenticated:
            if request.method == 'POST':
                comment = request.POST.get('comment')
                post = get_object_or_404(Post, pk=pk)
                comment = Comments(
                    post_pk=post,
                    comment=comment,
                    commenter=request.user,
                    date_commented=datetime.date.today()
                )
                comment.save()
            else:
                pass
        else:
            login_url = reverse('login') + f'?next={reverse("blog", args=[pk])}'
            return redirect(login_url)
        return redirect('blog', pk=pk)


class homeView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'all_blogs_list'

    def get_queryset(self):
        return Post.objects.order_by("-access_count")


class newBlogView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'new_blog.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentView(LoginRequiredMixin, CreateView):
    model = Comments
    template_name = 'blog.html'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        form.instance.date_commented = datetime.date().today()
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.object.pk
        return f'/post/{pk}/'


class updateBlogView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'update_blog.html'
    fields = ['title', 'body']


class deleteBlogView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('user')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())

@login_required
def dashboard_view(request):
    print('1')
    blog_list = Post.objects.filter(author=request.user)
    if request.method == 'POST':
        print('2')
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post(
                title=form.cleaned_data['title'],
                body=form.cleaned_data['body'],
                author=request.user
            )
            post.save()
        else:
            print(form.errors)
    else:
        form = PostForm()
    return render(request, 'user_dashboard.html', {'form': form, 'blog_list': blog_list})


class userBlogView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'all_blogs_list'
    template_name = 'user_posts.html'



# Create your views here.
