from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from dashboard.models import Course

@login_required
def course_detail(request, join_code):
    course = get_object_or_404(Course, join_code=join_code)
    return render(request, 'course/course_landing.html', {'course': course})

@login_required
def groups(request, join_code):
    return redirect('course_detail', join_code=join_code)