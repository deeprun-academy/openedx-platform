from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DeeprunCourseMeta, DeeprunProgress
from .serializers import DeeprunCourseMetaSerializer, DeeprunProgressSerializer

# A video is marked complete once the user has watched this fraction of its duration.
COMPLETION_RATIO = 0.9


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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def progress_upsert(request):
    """
    Upsert a single video's progress for a Clerk user.

    Body:
      clerk_user_id: str          (required)
      course_key: str             (required)
      vertical_id: str            (required)
      watched_seconds: int        (required) — highest playback position reached
      duration_seconds: int       (optional) — video length; captured on first heartbeat
      completed: bool             (optional) — explicit 'ended' event from the player

    watched_seconds is monotonic — we only ever increase it, so a seek back
    doesn't erase progress. 'completed' stays True once set.
    """
    clerk_user_id = (request.data.get("clerk_user_id") or "").strip()
    course_key = (request.data.get("course_key") or "").strip()
    vertical_id = (request.data.get("vertical_id") or "").strip()

    if not (clerk_user_id and course_key and vertical_id):
        return Response(
            {"error": "clerk_user_id, course_key, and vertical_id are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        watched = max(0, int(request.data.get("watched_seconds") or 0))
        duration = max(0, int(request.data.get("duration_seconds") or 0))
    except (TypeError, ValueError):
        return Response(
            {"error": "watched_seconds and duration_seconds must be integers"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    explicit_completed = bool(request.data.get("completed"))

    row, _ = DeeprunProgress.objects.get_or_create(
        clerk_user_id=clerk_user_id,
        course_key=course_key,
        vertical_id=vertical_id,
    )

    # Monotonic watched_seconds — a user seeking back shouldn't erase progress
    row.watched_seconds = max(row.watched_seconds, watched)
    # Capture or refresh duration if we didn't know it yet or it grew
    if duration and duration > row.duration_seconds:
        row.duration_seconds = duration

    if not row.completed:
        if explicit_completed:
            row.completed = True
        elif row.duration_seconds > 0 and row.watched_seconds >= row.duration_seconds * COMPLETION_RATIO:
            row.completed = True

    row.save()

    return Response(DeeprunProgressSerializer(row).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def progress_for_course(request, course_key):
    """
    Return all progress rows for a Clerk user in one course.

    Query params:
      clerk_user_id: str (required)

    Shape: [{ vertical_id, watched_seconds, duration_seconds, completed, last_accessed_at }]
    """
    clerk_user_id = (request.query_params.get("clerk_user_id") or "").strip()
    if not clerk_user_id:
        return Response({"error": "clerk_user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    rows = DeeprunProgress.objects.filter(
        clerk_user_id=clerk_user_id,
        course_key=course_key,
    )
    return Response(DeeprunProgressSerializer(rows, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_learning(request):
    """
    Return a compact list of courses the user has engaged with, most-recent first.

    Query params:
      clerk_user_id: str (required)
      limit:         int (optional, default 10)

    Each entry:
      course_key          — the course
      last_vertical_id    — most-recently-accessed video (resume target)
      last_accessed_at    — ISO timestamp
      completed_verticals — count of completed videos
      in_progress_verticals — count of non-completed videos touched
    """
    clerk_user_id = (request.query_params.get("clerk_user_id") or "").strip()
    if not clerk_user_id:
        return Response({"error": "clerk_user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        limit = max(1, min(50, int(request.query_params.get("limit") or 10)))
    except (TypeError, ValueError):
        limit = 10

    rows = (
        DeeprunProgress.objects
        .filter(clerk_user_id=clerk_user_id)
        .order_by("-last_accessed_at")
    )

    # Group by course_key in most-recent order, aggregate
    by_course: dict[str, dict] = {}
    for row in rows:
        entry = by_course.get(row.course_key)
        if entry is None:
            entry = {
                "course_key": row.course_key,
                "last_vertical_id": row.vertical_id,
                "last_accessed_at": row.last_accessed_at,
                "completed_verticals": 0,
                "in_progress_verticals": 0,
            }
            by_course[row.course_key] = entry
        if row.completed:
            entry["completed_verticals"] += 1
        else:
            entry["in_progress_verticals"] += 1

    result = list(by_course.values())[:limit]
    return Response(result)


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
