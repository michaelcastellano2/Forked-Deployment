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
   path('results/<str:course_code>/<str:delivery_number>/', views.peer_results, name='peer_results'),
   path('courses/<str:join_code>/create-form', views.create_form, name='create_form'),
   path('courses/<str:join_code>/create-form-info/<int:form_id>', views.create_form_info, name='create_form_info'),
   path('courses/<str:join_code>/create-form-questions/<int:form_id>', views.create_form_questions, name='create_form_questions'),
   path('courses/<str:join_code>/view-forms/', views.view_forms, name='view_forms'),
   path('courses/<str:join_code>/delete-form/<int:form_id>/', views.delete_form, name='delete_form'),
   path('courses/<str:join_code>/edit-form/<int:form_id>/', views.edit_form, name='edit_form')
]
