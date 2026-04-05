from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("deeprun_api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="deepruncoursemeta",
            name="instructor_avatar_url",
            field=models.CharField(
                blank=True,
                default="",
                help_text="URL to the instructor's photo (e.g. Open edX asset URL or external image)",
                max_length=1024,
            ),
        ),
    ]
