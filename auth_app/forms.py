import logging
import re
from typing import Dict, Any, List, Optional, Union, Type

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import FileExtensionValidator

from core.logging_utils import get_logger, log_user_activity, redact_sensitive_data

# Get a logger for this module
logger = get_logger(__name__)
from django.contrib.auth import authenticate
from users.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users with enhanced validation and logging."""
    
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
        'username_exists': "This username is already taken.",
        'email_exists': "This email address is already in use.",
        'password_too_short': "Password must be at least 8 characters long.",
        'password_too_common': "Password is too common or easily guessable.",
        'password_entirely_numeric': "Password cannot be entirely numeric.",
    }
    
    email = forms.EmailField(
        required=True,
        help_text="Enter a valid email address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.',
        }
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        error_messages={
            'required': 'Username is required.',
            'invalid': 'Please enter a valid username.',
            'max_length': 'Username is too long (maximum 150 characters).',
        },
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        error_messages={
            'required': 'First name is required.',
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        error_messages={
            'required': 'Password is required.',
        },
        help_text="Password must be at least 8 characters and cannot be entirely numeric."
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        error_messages={
            'required': 'Password confirmation is required.',
        },
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = CustomUser
        fields: List[str] = ['email', 'username', 'first_name', 'password1', 'password2']
        
    def clean_username(self) -> str:
        """
        Validate that the username is unique and properly formatted.
        
        Returns:
            The validated username
            
        Raises:
            forms.ValidationError: If the username is already in use or improperly formatted
        """
        username = self.cleaned_data.get('username')
        
        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(self.error_messages['username_exists'], code='username_exists')
            
        # Check for valid characters
        if username and not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError(
                'Username may only contain letters, numbers, and @/./+/-/_ characters.',
                code='invalid_username'
            )
            
        return username
        
    def clean_email(self) -> str:
        """
        Validate that the email is unique and properly formatted.
        
        Returns:
            The validated email
            
        Raises:
            forms.ValidationError: If the email is already in use
        """
        email = self.cleaned_data.get('email')
        
        if email and CustomUser.objects.filter(email=email).exists():
            # Log duplicate email attempt
            logger.warning(
                f"Registration attempt with duplicate email: {email}",
                extra={
                    'email': email,
                    'action': 'registration_failed',
                    'reason': 'duplicate_email'
                }
            )
            raise forms.ValidationError(self.error_messages['email_exists'], code='email_exists')
            
        return email
        
    def save(self, commit: bool = True) -> Any:
        """
        Save the form data to create a new user.
        
        Args:
            commit: Whether to save the model instance to the database
            
        Returns:
            The saved user instance
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        if commit:
            user.save()
            
            # Log user registration
            logger.info(
                f"New user registered: {user.username}",
                extra={
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'action': 'user_registration'
                }
            )
            
            # Log user activity
            log_user_activity(
                logger=logger,
                user_id=user.id,
                action="account_created",
                details={
                    'username': user.username,
                    'email': user.email
                }
            )
            
        return user


class CustomUserLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive. Please contact support for assistance.",
    }
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        label="Username",
        error_messages={
            'required': 'Username is required.',
            'invalid': 'Please enter a valid username.',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label="Password",
        error_messages={
            'required': 'Password is required.',
        }
    )
    
    def clean(self) -> Dict[str, Any]:
        """
        Override the default clean method to provide more specific error messages.
        
        Returns:
            The cleaned data dictionary
            
        Raises:
            forms.ValidationError: If authentication fails
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                # Check if the user exists but password is wrong
                if CustomUser.objects.filter(username=username).exists():
                    # Log failed login with incorrect password
                    logger.warning(
                        f"Failed login attempt for username: {username} (incorrect password)",
                        extra={
                            'username': username,
                            'action': 'login_failed',
                            'reason': 'incorrect_password'
                        }
                    )
                    raise forms.ValidationError(
                        "The password you entered is incorrect. Please try again.",
                        code='incorrect_password'
                    )
                else:
                    # Log failed login with non-existent user
                    logger.warning(
                        f"Failed login attempt for non-existent username: {username}",
                        extra={
                            'username': username,
                            'action': 'login_failed',
                            'reason': 'user_not_found'
                        }
                    )
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login'
                    )
            elif not self.user_cache.is_active:
                # Log failed login for inactive account
                logger.warning(
                    f"Login attempt for inactive account: {username}",
                    extra={
                        'username': username,
                        'user_id': self.user_cache.id,
                        'action': 'login_failed',
                        'reason': 'account_inactive'
                    }
                )
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive'
                )
            else:
                # Log successful login
                logger.info(
                    f"Successful login for user: {username}",
                    extra={
                        'username': username,
                        'user_id': self.user_cache.id,
                        'action': 'login_success'
                    }
                )
                
                # Log user activity
                log_user_activity(
                    logger=logger,
                    user_id=self.user_cache.id,
                    action="user_login",
                    details={
                        'username': username
                    }
                )
        return self.cleaned_data