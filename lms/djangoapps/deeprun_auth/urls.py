from django.urls import path
from .views import lms_login_view

urlpatterns = [
    path('login', lms_login_view, name='deeprun_login'),
]
