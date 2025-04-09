from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from dashboard.models import Course
from accounts.models import CustomUser
from .models import CourseForm, Team

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
    course = get_object_or_404(Course, join_code=join_code)

    if request.method == "POST":
        name = request.POST.get("form_name", "Untitled Form")
        self_evaluate = "self_evaluate" in request.POST
        num_likert = int(request.POST.get("num_likert", 0))
        num_open_ended = int(request.POST.get("num_open_ended", 0))
        due_date = request.POST.get("due_date")
        due_time = request.POST.get("due_time")

        course_form = CourseForm.objects.create(
            course=course,
            name=name,
            self_evaluate=self_evaluate,
            num_likert=num_likert,
            num_open_ended=num_open_ended,
            due_date=due_date,
            due_time=due_time,
        )
        course_form.save()

        return redirect('draft_questions', join_code=join_code, course_form_id=course_form.pk)
    
    return render(request, 'course/manage_forms.html', {'course': course})

@login_required
def draft_questions(request, join_code, course_form_id):
    course = get_object_or_404(Course, join_code=join_code)
    course_form = get_object_or_404(CourseForm, pk=course_form_id)

    return render(request, 'course/draft_questions.html', {'course': course, 'course_form': course_form})

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
