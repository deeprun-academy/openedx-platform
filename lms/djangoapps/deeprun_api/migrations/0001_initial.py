from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DeeprunCourseMeta",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("course_key", models.CharField(db_index=True, help_text="Open edX course key, e.g. course-v1:org+number+run", max_length=255, unique=True)),
                ("instructor_name", models.CharField(blank=True, default="", help_text="Display name for the instructor (e.g. 'Rick Astley')", max_length=255)),
                ("description", models.TextField(blank=True, default="", help_text="Short course description shown on the course card")),
                ("tags", models.JSONField(blank=True, default=list, help_text="List of tag strings, e.g. ['Fundamental', 'Preflop']")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "deeprun_course_meta",
            },
        ),
    ]
