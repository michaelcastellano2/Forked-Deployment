from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from dashboard.models import Course
from accounts.models import CustomUser
from .models import CourseForm, Team, Likert, OpenEnded
from django.http import HttpResponseRedirect

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
    forms = CourseForm.objects.filter(course=course)

    # Default color values
    default_colors = {
        'color_1': "#872729",  # default color 1
        'color_2': "#C44B4B",  # default color 2
        'color_3': "#F2F0EF",  # default color 3
        'color_4': "#3D5A80",  # default color 4
        'color_5': "#293241",  # default color 5
    }

    if request.method == "POST":
        name = request.POST.get("form_name", "Untitled Form")
        self_evaluate = "self_evaluate" in request.POST
        num_likert = int(request.POST.get("num_likert", 0))
        num_open_ended = int(request.POST.get("num_open_ended", 0))
        due_date = request.POST.get("due_date")
        due_time = request.POST.get("due_time")
        
        # Get color values from POST request or use default
        color_1 = request.POST.get('color_1', default_colors['color_1'])
        color_2 = request.POST.get('color_2', default_colors['color_2'])
        color_3 = request.POST.get('color_3', default_colors['color_3'])
        color_4 = request.POST.get('color_4', default_colors['color_4'])
        color_5 = request.POST.get('color_5', default_colors['color_5'])

        course_form = CourseForm.objects.create(
            course=course,
            name=name,
            self_evaluate=self_evaluate,
            num_likert=num_likert,
            num_open_ended=num_open_ended,
            due_date=due_date,
            due_time=due_time,
            color_1=color_1,
            color_2=color_2,
            color_3=color_3,
            color_4=color_4,
            color_5=color_5,
        )
        course_form.save()

        return redirect('draft_questions', join_code=join_code, course_form_id=course_form.pk)

    # Pass the default color values to the template
    return render(request, 'course/manage_forms.html', {
        'course': course,
        'default_colors': default_colors,
        'forms': forms
    })

@login_required
def edit_info(request, join_code, course_form_id):
    course = get_object_or_404(Course, join_code=join_code)
    course_form = get_object_or_404(CourseForm, pk=course_form_id)
    forms = CourseForm.objects.filter(course=course)

    default_colors = {
        'color_1': "#872729",  # default color 1
        'color_2': "#C44B4B",  # default color 2
        'color_3': "#F2F0EF",  # default color 3
        'color_4': "#3D5A80",  # default color 4
        'color_5': "#293241",  # default color 5
    }

    if request.method == "POST":
        modified_num_likert = int(request.POST.get("num_likert", course_form.num_likert))
        if modified_num_likert < course_form.num_likert:
            Likert.objects.filter(course_form=course_form, order__gte=modified_num_likert).delete()
        
        modified_num_open_ended = int(request.POST.get("num_open_ended", course_form.num_open_ended))
        if modified_num_open_ended < course_form.num_open_ended:
            OpenEnded.objects.filter(course_form=course_form, order__gte=modified_num_open_ended).delete()
        
        course_form.name = request.POST.get("form_name", course_form.name)
        course_form.self_evaluate = "self_evaluate" in request.POST
        course_form.num_likert = modified_num_likert
        course_form.num_open_ended = modified_num_open_ended
        course_form.due_date = request.POST.get("due_date", course_form.due_date)
        course_form.due_time = request.POST.get("due_time", course_form.due_time)
        course_form.color_1 = request.POST.get("color_1", course_form.color_1)
        course_form.color_2 = request.POST.get("color_2", course_form.color_2)
        course_form.color_3 = request.POST.get("color_3", course_form.color_3)
        course_form.color_4 = request.POST.get("color_4", course_form.color_4)
        course_form.color_5 = request.POST.get("color_5", course_form.color_5)
        course_form.save()

        return redirect('draft_questions', join_code=join_code, course_form_id=course_form.pk)
    
    return render(request, 'course/manage_forms.html', {
        'course': course,
        'default_colors': default_colors,
        'forms': forms,
        'course_form': course_form,
    })

@login_required
def draft_questions(request, join_code, course_form_id):
    course = get_object_or_404(Course, join_code=join_code)
    course_form = get_object_or_404(CourseForm, pk=course_form_id)
    course_forms = CourseForm.objects.filter(course=course)

    likert_qs = list(course_form.likert_questions.all().order_by('order'))
    open_ended_qs = list(course_form.open_ended_questions.all().order_by('order'))

    if request.method == "POST":
        if request.POST.get('action') == 'add_likert':
            course_form.num_likert += 1
            course_form.save()

            scroll_target = "scroll-likert"
            return HttpResponseRedirect(f'{request.path}#{scroll_target}')

        elif request.POST.get('action') == 'add_open_ended':
            course_form.num_open_ended += 1
            course_form.save()
            
            scroll_target = "scroll-open-ended"
            return HttpResponseRedirect(f'{request.path}#{scroll_target}')

        elif request.POST.get('action') == 'save':
            course_form.likert_questions.all().delete()
            course_form.open_ended_questions.all().delete()

            num_likert = course_form.num_likert
            for i in range(num_likert):
                question = request.POST.get(f"likert_question_{i}", "").strip()
                option_1 = request.POST.get(f"likert_{i}_label_1", "Strongly Disagree").strip()
                option_2 = request.POST.get(f"likert_{i}_label_2", "Disagree").strip()
                option_3 = request.POST.get(f"likert_{i}_label_3", "Neutral").strip()
                option_4 = request.POST.get(f"likert_{i}_label_4", "Agree").strip()
                option_5 = request.POST.get(f"likert_{i}_label_5", "Strongly Agree").strip()

                Likert.objects.create(
                    course_form=course_form,
                    question=question,
                    order=i,
                    option_1=option_1,
                    option_2=option_2,
                    option_3=option_3,
                    option_4=option_4,
                    option_5=option_5,
                )
            
            num_open_ended = course_form.num_open_ended
            for i in range(num_open_ended):
                question = request.POST.get(f"open_ended_question_{i}", "").strip()
                OpenEnded.objects.create(
                    course_form=course_form,
                    question=question,
                    order=i,    
                )

            course_form.save()
            scroll_target = "scroll-save"
            return HttpResponseRedirect(f"{request.path}#{scroll_target}")
        
        elif request.POST.get('action') == 'publish':
            course_form.state = 'published'
            course_form.save()
            return redirect('course_detail', join_code=join_code)
        
        elif request.POST.get('action') == 'release':
            course_form.state = 'released'
            course_form.save()
            return redirect('course_detail', join_code=join_code)

    context = {
        'course': course,
        'course_form': course_form,
        'forms': course_forms,
        'likert_qs': likert_qs,
        'open_ended_qs': open_ended_qs,
    }
    return render(request, 'course/draft_questions.html', context)

@login_required
def view_forms(request, join_code):
    course = get_object_or_404(Course, join_code=join_code)

    return render(request, "course/view_forms.html", {
        "join_code": join_code,
        "course": course,
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
        form.color_1 = request.POST.get('color_1')
        form.color_2 = request.POST.get('color_2')
        form.color_3 = request.POST.get('color_3')
        form.color_4 = request.POST.get('color_4')
        form.color_5 = request.POST.get('color_5')

        form.save() 
        messages.success(request, f"Form '{form.name}' has been updated successfully.")
        return redirect('view_forms', join_code=join_code)
    
    return render(request, 'course/edit_form.html', {
        'form': form,
        'course': course,
    })

def clear_course_forms(request, join_code):
    # Assuming you have a CourseForm model to clear forms
    try:
        course = Course.objects.get(join_code=join_code)
        # Assuming the course forms are related to the course
        CourseForm.objects.filter(course=course).delete()

        messages.success(request, 'All course forms have been cleared!')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found.')

    return redirect('course_detail', join_code=join_code)