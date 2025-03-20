from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden 
from accounts.models import CustomUser
from .models import Course 

@login_required
def dashboard(request):
    courses = request.user.enrolled_courses.all()
    return render(request, 'dashboard/dashboard.html', {'courses': courses})

@login_required
def join_course(request):
    if request.method == "POST":
        join_code = request.POST.get('join_code', '').strip()

        if len(join_code) != 6 or not join_code.isalnum():
            messages.error(request, "Invalid Code. Must be a 6-digit alphanumeric code.")
            return redirect('dashboard')
        
        try:
            course = Course.objects.get(join_code=join_code)
        except Course.DoesNotExist:
            messages.error(request, "A Course With This Code Does Not Exist.")
            return redirect('dashboard')
        
        if request.user.user_type != CustomUser.STUDENT:
            messages.error(request, "Joining a Course is Restricted ")
            return redirect('dashboard')

        if course.students.filter(pk=request.user.pk).exists():
            messages.info(request, f"Already enrolled in {course.title}.")
            return redirect('dashboard')

        course.students.add(request.user)
        course.student_count = course.students.count()
        course.save()

        messages.success(request, f"Successfully joined {course.title}!")
    return redirect('dashboard')