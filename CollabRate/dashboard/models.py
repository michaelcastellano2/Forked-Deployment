from django.db import models
from accounts.models import CustomUser #import the user model from accounts


class Course(models.Model):
   SEMESTER_CHOICES = [
       ('Spring', 'Spring'),
       ('Fall', 'Fall'),
   ]


   code = models.CharField(max_length=20) 
   title = models.CharField(max_length=100)
   student_count = models.IntegerField(default=0)
   semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
   year = models.IntegerField()


   #professor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'professor'})


   def __str__(self):
       return f"{self.code} - {self.title} ({self.semester} {self.year})"