from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired 
from django.urls import reverse
from django.conf import settings
from accounts.models import CustomUser
from .models import Course, Team
from .models import Course, CourseForm
import json
from django.http import HttpRequest
from datetime import date,time



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
        color = request.POST.get('color', '').strip()

        if not all([code, title, semester, year]):
            messages.error(request, "All fields are required.")
            return redirect('dashboard')
        
        # Prevent duplicate course identifiers
        if Course.objects.filter(code__iexact=code, semester__iexact=semester, year=year).exists():
            messages.error(request, f"{code} already exists.")
            return redirect('dashboard')
        
        course = Course(code=code, title=title, semester=semester, year=int(year), color=color, professor=request.user)
        course.save()

        raw_emails = request.POST.get('invite_email', '[]')
        try:
            emails = json.loads(raw_emails)
        except ValueError:
            emails = []
        
        signer = TimestampSigner()
        for email in emails:
            email = email.get('value', '').strip()
            if not email.lower().endswith('@bc.edu'):
                continue
            token = signer.sign(email)
            invite_url = request.build_absolute_uri(
                reverse('course_invite', args=[course.join_code, token])
            )
            subject = f"Invitation to join {course.title}"
            message = (
                f"Hello,\n\n"
                f"You have been invited to join the course \"{course.title}\".\n\n"
                f"Click the following link to join the course:\n{invite_url}\n\n"
                "If you did not expect this invitation, please ignore this email.\n\n"
                "Thank you!"
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)
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

@login_required
def course_invite(request, join_code, token):
    signer = TimestampSigner()
    try:
        invited_email = signer.unsign(token, max_age=3600)
    except SignatureExpired:
        messages.error(request, "The invitation link has expired.")
        return redirect('dashboard')
    except BadSignature:
        messages.error(request, "Invalid invitation link.")
        return redirect('dashboard')
    
    course = get_object_or_404(Course, join_code=join_code)
    if request.user.email.lower() != invited_email.lower():
        messages.error(request, "The invitation link is intended for a different account. Please sign in with the correct email.")
        return redirect('dashboard')
    if course.students.filter(pk=request.user.pk).exists():
        messages.info(request, f"Already enrolled in {course.title}")
    else:
        course.students.add(request.user)
        course.student_count = course.students.count()
        course.save()
        messages.success(request, f"Successfully enrolled in {course.title}.")

    return redirect('dashboard')

#Creating and Joining a Team

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
            return render(request, "dashboard/create_team.html", {
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
    return render(request, "dashboard/create_team.html", {
        "course": course,
        "students": course.students.all()
    })
def peer_results(request, course_code, delivery_number):
    # dummy data for now
    context = {
        'course_code': course_code,
        'delivery': delivery_number,
        'score': 9.6,
        'feedback': """Good job presenting his part of the presentation. Worked well with others when putting together submission and slides.
        Good time management, flexible with my scheduling conflicts, confident while speaking. Good teamwork/communication.
        Very communicative. Will and I collaborated together on the functional requirements..."""
    }
    return render(request, 'dashboard/peer_results.html', context)

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
    
    return render(request, 'dashboard/create_form_info.html', {'course': course, 'form_id': form_id})

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

    return render(request, 'dashboard/create_form_questions.html', {
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

    return render(request, "dashboard/view_forms.html", {
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
    
    return render(request, 'dashboard/edit_form.html', {
        'form': form,
        'course': course,
    })
