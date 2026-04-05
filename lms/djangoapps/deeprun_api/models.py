from django.db import models


class DeeprunCourseMeta(models.Model):
    """
    Stores custom course metadata for Deeprun Academy.
    Supplements Open edX course data with instructor display name,
    short description, and tags.
    """

    course_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Open edX course key, e.g. course-v1:org+number+run",
    )
    instructor_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Display name for the instructor (e.g. 'Rick Astley')",
    )
    instructor_avatar_url = models.CharField(
        max_length=1024,
        blank=True,
        default="",
        help_text="URL to the instructor's photo (e.g. Open edX asset URL or external image)",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Short course description shown on the course card",
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tag strings, e.g. ['Fundamental', 'Preflop']",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "deeprun_api"
        db_table = "deeprun_course_meta"

    def __str__(self):
        return f"{self.course_key} — {self.instructor_name}"
