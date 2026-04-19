"""
Ensure VideoUploadsEnabledByDefault is enabled platform-wide.

Studio hides the "Video Uploads" link in the Content menu unless
``context_course.video_pipeline_configured`` is True, which requires the
``VideoUploadsEnabledByDefault`` ConfigurationModel to be enabled with
``enabled_for_all_courses=True``. Fresh environments start with the flag
disabled, so Studio silently loses the menu until an operator enables it.

This data migration inserts an enabled row if the current latest row is
missing or disabled. ConfigurationModel treats the newest row as
authoritative, so appending a row is always safe — the check merely avoids
redundant inserts on environments that are already enabled (e.g. dev).
"""
from django.db import migrations


def enable_video_uploads_by_default(apps, schema_editor):
    Model = apps.get_model("video_pipeline", "VideoUploadsEnabledByDefault")
    latest = Model.objects.order_by("-change_date").first()
    if latest is None or not (latest.enabled and latest.enabled_for_all_courses):
        Model.objects.create(enabled=True, enabled_for_all_courses=True)


def noop(apps, schema_editor):
    # Reverse intentionally does nothing: rolling back should not disable the
    # flag on environments that rely on it. Operators can flip the flag via
    # Django admin if they really need to revert.
    return


class Migration(migrations.Migration):

    dependencies = [
        ("video_pipeline", "0003_coursevideouploadsenabledbydefault_videouploadsenabledbydefault"),
    ]

    operations = [
        migrations.RunPython(enable_video_uploads_by_default, noop),
    ]
