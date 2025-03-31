from django.urls import path
from . import views


urlpatterns = [
   path('', views.dashboard, name='dashboard'),
   path('courses/join/', views.join_course, name='join_course'),
   path('courses/create/', views.create_course, name='create_course'),
   path('courses/create/<str:join_code>/', views.create_team, name='create_team'),
   path('courses/leave/<str:join_code>/', views.leave_course, name='leave_course'),
   path('courses/delete/<str:join_code>/', views.delete_course, name='delete_course'),
   path('courses/invite/<str:join_code>/<str:token>/', views.course_invite, name='course_invite'),
   path('courses/<str:join_code>/team/create/', views.create_team, name='create_team'),
]
