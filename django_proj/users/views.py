from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from blog.models import Post
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    paginate_by = 2
    if request.method == 'POST':
        paginate_by = 2
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES,
                                        instance=request.user.profile)

   
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        
        # user = User.objects.filter(username=request.user).first()
        posts = Post.objects.filter(author=request.user)
        paginate_by = 2

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'posts': posts
    }
    return render(request, 'profile.html', context)

# def user_posts(request):
#     if request.method == 'POST':
#         user = User.objects.filter(username=request.user).post_set.all()
#         print(user)
#         paginate_by = 3 
#         context = {
#             'user_post': user
#         }
#         return render(request, 'profile.html', context)
