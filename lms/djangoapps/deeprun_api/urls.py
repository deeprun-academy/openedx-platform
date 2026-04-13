from django.urls import path

from . import views

urlpatterns = [
    path("api/deeprun/v1/course-meta/", views.course_meta_list, name="deeprun-course-meta-list"),
    path("api/deeprun/v1/course-meta/<path:course_key>", views.course_meta_detail, name="deeprun-course-meta-detail"),
    path("api/deeprun/v1/course/<path:course_key>", views.course_delete, name="deeprun-course-delete"),
    path("api/deeprun/v1/progress/", views.progress_upsert, name="deeprun-progress-upsert"),
    path("api/deeprun/v1/progress/<path:course_key>", views.progress_for_course, name="deeprun-progress-for-course"),
    path("api/deeprun/v1/my-learning/", views.my_learning, name="deeprun-my-learning"),
]
