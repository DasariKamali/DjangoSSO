from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login as django_login, logout as django_logout
from django.utils.timezone import now
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User  # Add this import
import binascii
import os
import logging

logger = logging.getLogger(__name__)

def home(request):
    # Render the home page with a login link
    return render(request, 'sso/home.html')

def login_successful(request):
    # Log basic failure info
    logger.debug(f"Login failed at {now()}.")
    
    # Render failure message
    context = {'message': 'We were unable to log you in using Microsoft SSO.'}
    return render(request, 'sso/login_successful.html', context)

@csrf_exempt
def microsoft_sso_callback(request):
    # Log basic info for debugging
    logger.debug(f"SSO callback triggered at {now()}")

    # Retrieve state from the callback and session
    state = request.GET.get('state')
    session_state = request.session.get('oauth2_state')

    # Check for state mismatch or missing state
    if not state or state != session_state:
        logger.error(f"State mismatch or state missing. Received: {state}, Expected: {session_state}")
        request.session.flush()  # Clear session to test if a fresh session resolves it
        return redirect(reverse('login_successful'))

    # Process the Microsoft user data
    microsoft_user = getattr(request, 'microsoft_user', None)

    if microsoft_user:
        email = microsoft_user.get('email')

        if email:
            try:
                user = User.objects.get(email=email)
                # Log the user in using the correct backend
                django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('admin:index')
            except User.DoesNotExist:
                return redirect(reverse('login_successful'))
        else:
            return redirect(reverse('login_successful'))
    else:
        return redirect(reverse('login_successful'))

def sso_login(request):
    # Generate a secure random state
    state = binascii.hexlify(os.urandom(16)).decode()
    
    # Store state in session and save
    request.session['oauth2_state'] = state
    request.session.save()

    # Build the Microsoft login URL
    login_url = f'https://login.microsoftonline.com/{settings.MICROSOFT_SSO_TENANT_ID}/oauth2/v2.0/authorize'
    
    params = {
        'client_id': settings.MICROSOFT_SSO_APPLICATION_ID,
        'response_type': 'code',
        'redirect_uri': settings.MICROSOFT_SSO_REDIRECT_URI,
        'response_mode': 'query',
        'scope': ' '.join(settings.MICROSOFT_SSO_SCOPES),
        'state': state,
    }

    login_url_with_params = f"{login_url}?{'&'.join(f'{key}={value}' for key, value in params.items())}"

    return redirect(login_url_with_params)

def logout(request):
    # Log out the user and redirect to home
    django_logout(request)
    return redirect('home')
