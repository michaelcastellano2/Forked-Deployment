from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden 
from accounts.models import CustomUser
from .models import Course 
import json

@login_required
def dashboard(request):
    if request.user.user_type == CustomUser.PROFESSOR:
        courses = request.user.courses.all()
    elif request.user.user_type == CustomUser.STUDENT:
        courses = request.user.enrolled_courses.all()
    else:
        courses = Course.objects.none()
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
            messages.error(request, "Joining a course is restricted to students.")
            return redirect('dashboard')

        if course.students.filter(pk=request.user.pk).exists():
            messages.info(request, f"Already enrolled in {course.title}.")
            return redirect('dashboard')

        course.students.add(request.user)
        course.student_count = course.students.count()
        course.save()

        messages.success(request, f"Successfully joined {course.title}!")
    return redirect('dashboard')

@login_required
def create_course(request):
    if request.method == "POST":
        code = request.POST.get('code', '').strip()
        title = request.POST.get('title', '').strip()
        semester = request.POST.get('semester')
        year = request.POST.get('year')

        if not all([code, title, semester, year]):
            messages.error(request, "All fields are required.")
            return redirect('dashboard')
        
        # Prevent duplicate course identifiers
        if Course.objects.filter(code__iexact=code, semester__iexact=semester, year=year).exists():
            messages.error(request, f"{code} already exists.")
            return redirect('dashboard')
        
        course = Course(code=code, title=title, semester=semester, year=int(year), professor=request.user)
        course.save()

        raw_emails = request.POST.get('invite_email', '[]')
        try:
            emails = json.loads(raw_emails)
        except ValueError:
            emails = []
        
        for email in emails:
            if not email['value'].lower().endswith('@bc.edu'):
                continue
            print(email)
        messages.success(request, f"Course {course.title} created. Join Code: {course.join_code}")
    return redirect('dashboard')

@login_required
def leave_course(request, join_code):
    if request.user.user_type != CustomUser.STUDENT:
        messages.error(request, "Leaving a course is restricted to students.")
        return redirect('dashboard')
    course = get_object_or_404(Course, join_code=join_code)
    course.students.remove(request.user)
    messages.success(request, f"Unenrolled from {course.title}.")
    return redirect('dashboard')

@login_required
def delete_course(request, join_code):
    try:
        course = Course.objects.get(join_code=join_code, professor=request.user)
    except Course.DoesNotExist():
        messages.error(request, "Course not found. Do not have permission to delete a course.")
    else:
        title = course.title
        course.delete()
        messages.success(request, f"Course {title} has been deleted.")
    return redirect('dashboard')
    