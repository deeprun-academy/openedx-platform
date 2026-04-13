from rest_framework import serializers

from .models import DeeprunCourseMeta, DeeprunProgress


class DeeprunCourseMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeeprunCourseMeta
        fields = ["course_key", "instructor_name", "instructor_avatar_url", "description", "tags", "updated_at"]
        read_only_fields = ["updated_at"]


class DeeprunProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeeprunProgress
        fields = [
            "course_key",
            "vertical_id",
            "watched_seconds",
            "duration_seconds",
            "completed",
            "last_accessed_at",
        ]
        read_only_fields = ["last_accessed_at"]
