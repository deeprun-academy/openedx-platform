from django.urls import path

from . import views

urlpatterns = [
    path("api/deeprun/v1/course-meta/", views.course_meta_list, name="deeprun-course-meta-list"),
    path("api/deeprun/v1/course-meta/<path:course_key>", views.course_meta_detail, name="deeprun-course-meta-detail"),
]
