from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DeeprunCourseMeta
from .serializers import DeeprunCourseMetaSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def course_meta_list(request):
    """List metadata for all courses."""
    metas = DeeprunCourseMeta.objects.all()
    serializer = DeeprunCourseMetaSerializer(metas, many=True)
    return Response(serializer.data)


@api_view(["GET", "PUT", "POST"])
@permission_classes([IsAuthenticated])
def course_meta_detail(request, course_key):
    """Get or create/update metadata for a specific course."""
    if request.method == "GET":
        try:
            meta = DeeprunCourseMeta.objects.get(course_key=course_key)
        except DeeprunCourseMeta.DoesNotExist:
            return Response(
                {"course_key": course_key, "instructor_name": "", "description": "", "tags": [], "updated_at": None}
            )
        serializer = DeeprunCourseMetaSerializer(meta)
        return Response(serializer.data)

    # PUT or POST — create or update
    meta, _created = DeeprunCourseMeta.objects.get_or_create(course_key=course_key)
    serializer = DeeprunCourseMetaSerializer(meta, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
