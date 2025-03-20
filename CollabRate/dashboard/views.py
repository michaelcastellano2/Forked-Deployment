from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden 
from accounts.models import CustomUser
from .models import Course 

@login_required
def dashboard(request):
    courses = request.user.enrolled_courses.all()
    return render(request, 'dashboard/dashboard.html', {'courses': courses})

@login_required
def join_course(request):
    return redirect('dashboard')