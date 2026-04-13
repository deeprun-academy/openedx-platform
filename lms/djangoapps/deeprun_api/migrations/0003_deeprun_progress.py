from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("deeprun_api", "0002_instructor_avatar_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeeprunProgress",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("clerk_user_id", models.CharField(db_index=True, help_text="Clerk user id, e.g. user_2abc...", max_length=64)),
                ("course_key", models.CharField(db_index=True, help_text="Open edX course key, e.g. course-v1:org+number+run", max_length=255)),
                ("vertical_id", models.CharField(help_text="Block usage key of the vertical that contains the video", max_length=255)),
                ("watched_seconds", models.PositiveIntegerField(default=0, help_text="Highest playback position the user has reached, in seconds")),
                ("duration_seconds", models.PositiveIntegerField(default=0, help_text="Video duration, in seconds (captured on first heartbeat)")),
                ("completed", models.BooleanField(default=False, help_text="True once watched >= 90% of duration or the player fired 'ended'")),
                ("last_accessed_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "deeprun_progress",
                "unique_together": {("clerk_user_id", "course_key", "vertical_id")},
            },
        ),
        migrations.AddIndex(
            model_name="deeprunprogress",
            index=models.Index(fields=["clerk_user_id", "-last_accessed_at"], name="deeprun_prog_user_recent_idx"),
        ),
    ]
