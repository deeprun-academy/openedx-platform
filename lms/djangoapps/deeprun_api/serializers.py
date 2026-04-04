from rest_framework import serializers

from .models import DeeprunCourseMeta


class DeeprunCourseMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeeprunCourseMeta
        fields = ["course_key", "instructor_name", "description", "tags", "updated_at"]
        read_only_fields = ["updated_at"]
