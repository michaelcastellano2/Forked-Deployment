from django.urls import path
from . import views


urlpatterns = [
   path('', views.dashboard, name='dashboard'),
   path('join-course/', views.join_course, name='join_course'),
]
