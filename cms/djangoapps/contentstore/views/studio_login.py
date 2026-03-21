"""
Deeprun Academy — Custom Studio Login View

Provides a direct login form on Studio's domain instead of
redirecting to LMS for OAuth. Works because CMS and LMS share
the same Django user database.
"""

import logging

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from common.djangoapps.student.models import Registration

log = logging.getLogger(__name__)


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def studio_login_view(request):
    """
    Custom login view for Studio.
    GET: renders the login form.
    POST: authenticates and redirects to Studio home.
    """
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', '/home/'))

    error_message = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '/home/')

        if not email or not password:
            error_message = 'Please enter both email and password.'
        else:
            # Look up user by email to get username (Django authenticates by username)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                username = email  # fallback, will fail auth

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    error_message = 'Your account is not active. Please contact support.'
                elif not (user.is_staff or user.is_superuser):
                    error_message = 'You do not have permission to access Studio.'
                else:
                    login(request, user)
                    log.info('Studio login successful for user: %s', user.username)
                    return redirect(next_url)
            else:
                error_message = 'Invalid email or password.'

    next_url = request.GET.get('next', '/home/')
    platform_name = getattr(settings, 'PLATFORM_NAME', 'Open edX')

    return render(request, 'studio_login.html', {
        'error_message': error_message,
        'next_url': next_url,
        'platform_name': platform_name,
        'csrf_token': get_token(request),
    })
