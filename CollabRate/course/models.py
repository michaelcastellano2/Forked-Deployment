import random
import string
from django.db import models
from dashboard.models import Course
from accounts.models import CustomUser


class CourseForm(models.Model):
    form_id = models.CharField(max_length=6, primary_key=True, unique=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Untitled form")
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)
    num_likert = models.PositiveIntegerField(default=3)
    num_open = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    self_evaluate = models.BooleanField(default=False)
    likert_questions = []
    open_questions = []

    def generate_form_id(self):
        return ''.join(random.choices(string.digits, k=6))

    def save(self, *args, **kwargs):
        if not self.form_id:
            self.form_id = self.generate_form_id()
            while CourseForm.objects.filter(form_id=self.form_id).exists():
                self.form_id = self.generate_form_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"Form ID: {self.form_id}, "
                f"Course: {self.course.title}, "
                f"Name: {self.name}, "
                f"Due Date: {self.due_date}, "
                f"Due Time: {self.due_time}, "
                f"Likert Questions: {self.num_likert}, "
                f"Open-ended Questions: {self.num_open}, "
                f"Created At: {self.created_at}, "
                f"Self Evaluate: {self.self_evaluate}")
                
class Team(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(
        Course, 
        on_delete = models.CASCADE, 
        related_name = 'teams'
    )
    students = models.ManyToManyField(
        CustomUser, 
        limit_choices_to={'user_type': CustomUser.STUDENT},
        related_name = 'teams',
        blank = True
    )

    def _str_(self): 
        return f"{self.name} (Course: {self.course.code})"
    

