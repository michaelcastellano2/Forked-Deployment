from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomSocialSignupForm

def custom_social_signup(request):
    if request.method == 'POST':
        form = CustomSocialSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            print(user)
            messages.success(request, "Signup Complete. Welcome!")
            return redirect('/')
        else:
            messages.error(request, "Error with Submission.")
    else:
        form = CustomSocialSignupForm()
    return render(request, 'socialaccount/signup.html', {'form': form})

