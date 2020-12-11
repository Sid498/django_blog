from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.views.decorators.csrf import csrf_exempt
from blog_api.serializers import BlogSerializer
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from .forms import ContactForm
from django.urls import reverse_lazy, reverse
from .models import Post
import os


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context=context)


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_post.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')
        

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    # def post(self, request, *args, **kwargs):
    #     return HttpResponseRedirect(reverse('home'))
    
    def get_context_data(self, **kwargs):
        if self.request.method == "POST":
            print("method called")
        context = super().get_context_data(**kwargs)
        data = get_object_or_404(Post, id=self.kwargs['pk'])
        total_likes = data.total_likes()
        # if self.request.method == 'POST':
        liked = False
        if data.likes.filter(id=self.request.user.id).exists():
            liked = True
        else:
            pass

        context["total_likes"] = total_likes
        context["liked"] = liked
        return context
    


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_create.html'
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message +" "+ from_email, os.environ.get('EMAIL_USER'), ["your_company_mail_here"]) #put reciever mail
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
    return render(request, "blog/email.html", {'form': form})

def successView(request):
    return render(request, "blog/email_sent.html")

@api_view(['GET'])
@csrf_exempt
def view_post(request,post_id=None):
    if not post_id:
        if request.method == 'GET':
            queryset = Post.objects.all()
            serializer = BlogSerializer(queryset, many=True)
    else:
        try:
            queryset = Post.objects.filter(id=post_id)
            serializer = BlogSerializer(queryset, many=True)
        except Exception:
            raise Http404('Post not found')
    return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
@csrf_exempt
def add_post(request):
    serializer = BlogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status":"post created"}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(serializer.data, safe=False)

@login_required
def LikeView(request,pk):
    # post = get_object_or_404(Post, id=request.POST.get('post_id'))
    post = Post.objects.get(id=pk)
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('post_detail', args=[str(pk)]))
