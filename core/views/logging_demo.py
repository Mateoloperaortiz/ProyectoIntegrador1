"""
Demo views for showcasing the enhanced logging system.

These views are for demonstration purposes only and should not be used in production.
"""
import logging
import time
from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from core.logging_utils import (
    LoggingMixin,
    get_logger,
    log_exception,
    log_user_activity,
)
from auth_app.forms import CustomUserLoginForm  # Centralized in auth_app
from users.forms import UserProfileForm

# Get a logger for this module
logger = get_logger(__name__)


@require_http_methods(["GET"])
def logging_demo_basic(request: HttpRequest) -> HttpResponse:
    """
    A simple view that demonstrates basic logging functionality.
    
    This view logs messages at different levels and returns a simple response.
    """
    # Log at different levels
    logger.debug("This is a DEBUG message from the demo view")
    logger.info("User accessed the logging demo view")
    logger.warning("This is a WARNING message for demonstration")
    
    # Include structured data in logs
    logger.info(
        "Structured log message",
        extra={
            "user_id": request.user.id if request.user.is_authenticated else None,
            "ip_address": request.META.get("REMOTE_ADDR", "unknown"),
            "path": request.path,
            "query_params": dict(request.GET.items()),
        },
    )
    
    # Log user activity if authenticated
    if request.user.is_authenticated:
        log_user_activity(
            logger=logger,
            user_id=request.user.id,
            action="viewed_logging_demo",
            details={"path": request.path},
            ip_address=request.META.get("REMOTE_ADDR", "unknown"),
        )
    
    return render(request, "core/logging_demo.html", {
        "title": "Logging Demo",
        "message": "Check the logs to see the logged messages",
    })


@require_http_methods(["GET"])
def logging_demo_error(request: HttpRequest) -> HttpResponse:
    """
    A view that demonstrates error logging.
    
    This view intentionally raises an exception to demonstrate error logging.
    """
    logger.info("User accessed the error logging demo view")
    
    try:
        # Intentionally cause an error
        value = int(request.GET.get("value", "abc"))  # This will raise ValueError for the default
        result = 100 / value  # This might raise ZeroDivisionError
        
        return JsonResponse({"result": result})
    
    except Exception as e:
        # Log the exception with context
        log_exception(
            logger=logger,
            exc=e,
            message="Error in logging demo view",
            extra={
                "path": request.path,
                "query_params": dict(request.GET.items()),
                "user_id": request.user.id if request.user.is_authenticated else None,
            },
        )
        
        # Re-raise to let Django handle the response
        raise


@login_required
@require_http_methods(["GET"])
def logging_demo_performance(request: HttpRequest) -> HttpResponse:
    """
    A view that demonstrates performance logging.
    
    This view simulates a slow operation and logs the performance metrics.
    """
    logger.info("User accessed the performance logging demo view")
    
    # Start timing
    start_time = time.time()
    
    # Simulate a slow operation
    duration = float(request.GET.get("duration", "1.0"))
    time.sleep(duration)
    
    # End timing and calculate duration
    elapsed_time = time.time() - start_time
    
    # Log performance metrics
    logger.info(
        f"Operation completed in {elapsed_time:.3f} seconds",
        extra={
            "duration": f"{elapsed_time:.3f}s",
            "operation": "sleep",
            "user_id": request.user.id,
            "path": request.path,
        },
    )
    
    # Log user activity
    log_user_activity(
        logger=logger,
        user_id=request.user.id,
        action="performance_test",
        details={
            "duration": f"{elapsed_time:.3f}s",
            "requested_duration": duration,
        },
        ip_address=request.META.get("REMOTE_ADDR", "unknown"),
    )
    
    return JsonResponse({
        "status": "success",
        "duration": f"{elapsed_time:.3f}s",
        "requested_duration": duration,
    })


class LoggingDemoClassView(LoggingMixin, object):
    """
    A class-based view that demonstrates using the LoggingMixin.
    
    This view logs messages using the logger provided by the mixin.
    """
    
    def __call__(self, request: HttpRequest, *args: Any, **kwargs: Dict[str, Any]) -> HttpResponse:
        """Handle the request and log using the mixin's logger."""
        self.logger.info("LoggingDemoClassView was called")
        
        # Log request details
        self.logger.debug(
            "Request details",
            extra={
                "method": request.method,
                "path": request.path,
                "user": request.user.username if request.user.is_authenticated else "Anonymous",
            },
        )
        
        # Simulate some processing
        self.logger.info("Processing request")
        time.sleep(0.5)
        self.logger.info("Request processing completed")
        
        return JsonResponse({
            "status": "success",
            "message": "Check the logs to see the logged messages",
            "view_type": "class_based",
        })


# Create an instance of the class-based view
logging_demo_class_view = LoggingDemoClassView()


@require_http_methods(["GET", "POST"])
def logging_demo_user_forms(request: HttpRequest) -> HttpResponse:
    """
    A view that demonstrates logging in user forms.
    
    This view shows how form validation and submission are logged.
    """
    logger.info(
        "User accessed the form logging demo view",
        extra={
            "user_id": request.user.id if request.user.is_authenticated else None,
            "ip_address": request.META.get("REMOTE_ADDR", "unknown"),
            "path": request.path,
        },
    )
    
    # Initialize forms
    login_form = CustomUserLoginForm()
    
    # If user is authenticated, show profile form instead
    profile_form = None
    if request.user.is_authenticated:
        profile_form = UserProfileForm(instance=request.user)
    
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        
        if form_type == "login" and not request.user.is_authenticated:
            # Process login form (demo only - not actually logging in)
            login_form = CustomUserLoginForm(data=request.POST)
            if login_form.is_valid():
                # In a real view, we would log in the user here
                # For demo purposes, we'll just show a success message
                messages.success(request, "Login form validated successfully. Check logs for details.")
                return redirect(reverse("core:logging_demo_user_forms"))
        
        elif form_type == "profile" and request.user.is_authenticated:
            # Process profile form (demo only - not actually saving)
            profile_form = UserProfileForm(data=request.POST, instance=request.user, files=request.FILES)
            if profile_form.is_valid():
                # For demo purposes, we'll validate but not save
                # In a real view, we would call profile_form.save()
                logger.info(
                    "Profile form validated successfully (demo only, not saved)",
                    extra={
                        "user_id": request.user.id,
                        "username": request.user.username,
                        "action": "profile_form_validated"
                    }
                )
                messages.success(request, "Profile form validated successfully. Check logs for details.")
                return redirect(reverse("core:logging_demo_user_forms"))
    
    return render(request, "core/logging_demo_forms.html", {
        "title": "User Forms Logging Demo",
        "login_form": login_form,
        "profile_form": profile_form,
    })
