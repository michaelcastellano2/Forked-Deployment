from django.urls import path
from . import views

urlpatterns = [
    path('<str:join_code>/', views.course_detail, name='course_detail'),
    path('<str:join_code>/groups/', views.groups, name='groups')
]