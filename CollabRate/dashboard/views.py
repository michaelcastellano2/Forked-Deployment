from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden 
from accounts.models import CustomUser #import the user model from accounts 
from .models import Course 

@login_required
def dashboard(request):
    #color choices for the dashboard
    courses = Course.objects.all() #Fetch all courses 
    return render(request, 'dashboard/dashboard.html', {'courses': courses})

