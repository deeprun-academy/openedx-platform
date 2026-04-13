from django.db import models


class DeeprunProgress(models.Model):
    """
    Per-user video watching progress, keyed on the Clerk user ID.

    We don't rely on Open edX per-user tracking because learners authenticate
    via Clerk and don't have edX accounts. One row per (user, course, vertical).
    """

    clerk_user_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Clerk user id, e.g. user_2abc...",
    )
    course_key = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Open edX course key, e.g. course-v1:org+number+run",
    )
    vertical_id = models.CharField(
        max_length=255,
        help_text="Block usage key of the vertical that contains the video",
    )
    watched_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Highest playback position the user has reached, in seconds",
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Video duration, in seconds (captured on first heartbeat)",
    )
    completed = models.BooleanField(
        default=False,
        help_text="True once watched >= 90% of duration or the player fired 'ended'",
    )
    last_accessed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "deeprun_api"
        db_table = "deeprun_progress"
        unique_together = [("clerk_user_id", "course_key", "vertical_id")]
        indexes = [
            models.Index(
                fields=["clerk_user_id", "-last_accessed_at"],
                name="deeprun_prog_user_recent_idx",
            ),
        ]

    def __str__(self):
        return f"{self.clerk_user_id} — {self.course_key} / {self.vertical_id}"


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
