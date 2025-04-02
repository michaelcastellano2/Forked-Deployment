from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from dashboard.models import Course
from accounts.models import CustomUser
from .models import CourseForm, Team
from datetime import date, time

@login_required
def course_detail(request, join_code):
    course = get_object_or_404(Course, join_code=join_code)
    return render(request, 'course/course_landing.html', {'course': course})

@login_required
def groups(request, join_code):
    return redirect('course_detail', join_code=join_code)

@login_required
def create_team(request, join_code):
    course = get_object_or_404(Course, join_code=join_code)
    user = request.user
    
    # Safeguard
    is_professor = (user == course.professor)
    is_enrolled = (
        user.user_type == CustomUser.STUDENT and
        course.students.filter(id=user.id).exists()
    )
    if not (is_professor or is_enrolled):
        return HttpResponseForbidden("You do not have permission to create a team for this course.")
    
    if request.method == "POST":
        team_name = request.POST.get("team_name", "")
        selected_ids = request.POST.getlist("students")
        
        if not team_name:
            messages.error(request, "Team name is required.")
            return render(request, "course/create_team.html", {
                "course": course,
                "students": course.students.all()
            })
        
        # Create new team
        team = Team.objects.create(name=team_name, course=course)
        enrolled_students = course.students.filter(id__in=selected_ids)
        team.students.set(enrolled_students)
        
        if is_enrolled and user not in team.students.all():
            team.students.add(user)
        
        messages.success(request, f"Team '{team.name}' created successfully.")
        return redirect('create_team', join_code=course.join_code)

    # GET request show the empty form
    return render(request, "course/create_team.html", {
        "course": course,
        "students": course.students.all()
    })


@login_required
def create_form(request, join_code):
    course = Course.objects.get(join_code=join_code)

    form = CourseForm(
    course=course,
    name="Untitled form",
    due_date=date.today(), 
    due_time=time(23, 59),        
    num_likert=3,
    num_open=1,
    self_evaluate=False
    )
    form.save()

    return redirect('create_form_info', join_code=join_code, form_id=form.form_id)

@login_required
def create_form_info(request, join_code, form_id):
    course = Course.objects.get(join_code=join_code)
    form = CourseForm.objects.get(form_id=form_id)

    if request.method == 'POST':
        return redirect('create_form_questions', 
            join_code=course.join_code,
            form=form)
    
    return render(request, 'course/create_form_info.html', {'course': course, 'form_id': form_id})

@login_required
def create_form_questions(request, join_code, form_id):
    course = Course.objects.get(join_code=join_code)
    form = CourseForm.objects.get(form_id=form_id)

    if request.method == "POST":

        form_name = request.POST.get('form_name', '')
        due_date = request.POST.get('due_date', '')
        due_time = request.POST.get('due_time', '')
        self_evaluate = 'self_evaluate' in request.POST
        num_likert = int(request.POST.get('num_likert', 3))
        num_open = int(request.POST.get('num_open', 1))

        form.name = form_name
        form.due_date = due_date
        form.due_time = due_time
        form.self_evaluate = self_evaluate
        form.num_likert = num_likert
        form.num_open = num_open
        form.course = course 

        form.save()

    return render(request, 'course/create_form_questions.html', {
        'join_code': join_code,
        'form_id': form_id,
        'range_likert': range(form.num_likert),
        'range_open': range(form.num_open),
        'course': course
    })

@login_required
def view_forms(request, join_code):
    course = get_object_or_404(Course, join_code=join_code)
    forms = CourseForm.objects.filter(course=course)  

    return render(request, "course/view_forms.html", {
        "join_code": join_code,
        "course": course,
        "forms": forms,  
    })

@login_required
def delete_form(request, join_code, form_id):
    course = get_object_or_404(Course, join_code=join_code)
    
    if request.method == "POST":
        form = get_object_or_404(CourseForm, form_id=form_id)
        form.delete()  
    
    return redirect('view_forms', join_code=join_code)

@login_required
def edit_form(request, join_code, form_id):
    course = get_object_or_404(Course, join_code=join_code)
    form = get_object_or_404(CourseForm, pk=form_id, course=course)
    
    if request.method == 'POST':
        form.name = request.POST.get('form_name')
        form.due_date = request.POST.get('due_date')
        form.due_time = request.POST.get('due_time')
        form.self_evaluate = 'self_evaluate' in request.POST

        form.save() 
        messages.success(request, f"Form '{form.name}' has been updated successfully.")
        return redirect('view_forms', join_code=join_code)
    
    return render(request, 'course/edit_form.html', {
        'form': form,
        'course': course,
    })
