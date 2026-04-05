from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DeeprunCourseMeta
from .serializers import DeeprunCourseMetaSerializer


class CsrfExemptSessionAuth(SessionAuthentication):
    """Session auth without CSRF enforcement (CSRF is handled by Django middleware)."""

    def enforce_csrf(self, request):
        return


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def course_meta_list(request):
    """List metadata for all courses."""
    metas = DeeprunCourseMeta.objects.all()
    serializer = DeeprunCourseMetaSerializer(metas, many=True)
    return Response(serializer.data)


@api_view(["GET", "PUT", "POST"])
@authentication_classes([CsrfExemptSessionAuth])
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


@api_view(["DELETE"])
@authentication_classes([CsrfExemptSessionAuth])
@permission_classes([IsAuthenticated])
def course_delete(request, course_key):
    """
    Delete a course from the modulestore and remove its Deeprun metadata.
    Requires staff permission on the course.
    """
    from cms.djangoapps.contentstore.utils import delete_course
    from common.djangoapps.student.auth import has_studio_write_access

    try:
        key = CourseKey.from_string(course_key)
    except InvalidKeyError:
        return Response({"error": "Invalid course key"}, status=status.HTTP_400_BAD_REQUEST)

    if not has_studio_write_access(request.user, key):
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    try:
        delete_course(key, request.user.id)
    except Exception as exc:  # noqa: BLE001
        return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Clean up Deeprun metadata
    DeeprunCourseMeta.objects.filter(course_key=course_key).delete()

    return Response({"deleted": course_key}, status=status.HTTP_200_OK)
