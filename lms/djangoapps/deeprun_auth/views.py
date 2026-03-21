"""
Deeprun Academy — Custom LMS Login View

Standard server-side login form that works in all browsers
including Brave (which blocks JS cookie access for CSRF).
"""

import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from common.djangoapps.student.models import Registration

log = logging.getLogger(__name__)
User = get_user_model()


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def lms_login_view(request):
    """
    Custom login view for LMS.
    GET: renders the login form.
    POST: authenticates and redirects to dashboard or next URL.
    """
    next_url = request.GET.get('next', request.POST.get('next', '/dashboard'))

    if request.user.is_authenticated:
        return redirect(next_url)

    error_message = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            error_message = 'Please enter both email and password.'
        else:
            # Look up user by email to get username
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                username = email  # fallback

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    error_message = 'Your account is not active. Please contact support.'
                else:
                    login(request, user)
                    log.info('LMS login successful for user: %s', user.username)
                    return redirect(next_url)
            else:
                error_message = 'Invalid email or password.'

    platform_name = getattr(settings, 'PLATFORM_NAME', 'Open edX')

    return render(request, 'deeprun_login.html', {
        'error_message': error_message,
        'next_url': next_url,
        'platform_name': platform_name,
    })
