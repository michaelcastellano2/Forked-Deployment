from django.urls import path
from .views import custom_social_signup

urlpatterns = [
    path('social/signup/', custom_social_signup, name='socialaccount_signup')
]