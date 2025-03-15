import logging
import re
from typing import Dict, Any, List, Optional, Union, Type

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import FileExtensionValidator

from core.logging_utils import get_logger, log_user_activity

# Get a logger for this module
logger = get_logger(__name__)
from django.contrib.auth import authenticate
from .models import CustomUser

# Import forms from auth_app (the source of truth)
from auth_app.forms import CustomUserCreationForm, CustomUserLoginForm

# Re-export auth_app forms for backward compatibility
# This approach maintains backward compatibility while eliminating duplicated code
# Any code using 'from users.forms import CustomUserCreationForm, CustomUserLoginForm'
# will still work, but will actually use the auth_app implementations


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original values for comparison in save method
        if self.instance and self.instance.pk:
            self.initial_data = {
                'email': self.instance.email,
                'first_name': self.instance.first_name,
                'last_name': self.instance.last_name,
                'bio': self.instance.bio
            }
    """
    Form for updating user profile information.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about yourself', 'rows': 3}),
        max_length=500,
        help_text="Maximum 500 characters"
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        help_text="Supported formats: JPG, JPEG, PNG, GIF. Max size: 5MB"
    )
    
    class Meta:
        model = CustomUser
        fields: List[str] = ['email', 'first_name', 'last_name', 'bio', 'profile_picture']
        
    def clean_email(self) -> str:
        """
        Validate that the email is unique and properly formatted.
        
        Returns:
            The validated email
            
        Raises:
            forms.ValidationError: If the email is already in use by another user or improperly formatted
        """
        email = self.cleaned_data.get('email')
        username = self.instance.username
        
        if email and CustomUser.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Email is already in use by another user.')
        
        # Additional validation for email format
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if email and not email_pattern.match(email):
            raise forms.ValidationError('Please enter a valid email address.')
            
        return email
    
    def clean_first_name(self) -> str:
        """
        Validate that the first name contains only letters and spaces.
        
        Returns:
            The validated first name
            
        Raises:
            forms.ValidationError: If the first name contains invalid characters
        """
        first_name = self.cleaned_data.get('first_name')
        
        if first_name and not all(c.isalpha() or c.isspace() for c in first_name):
            raise forms.ValidationError('First name should contain only letters and spaces.')
            
        return first_name
    
    def clean_last_name(self) -> str:
        """
        Validate that the last name contains only letters and spaces.
        
        Returns:
            The validated last name
            
        Raises:
            forms.ValidationError: If the last name contains invalid characters
        """
        last_name = self.cleaned_data.get('last_name')
        
        if last_name and not all(c.isalpha() or c.isspace() for c in last_name):
            raise forms.ValidationError('Last name should contain only letters and spaces.')
            
        return last_name
    
    def clean_profile_picture(self) -> Optional[Any]:
        """
        Validate that the profile picture is not too large.
        
        Returns:
            The validated profile picture
            
        Raises:
            forms.ValidationError: If the profile picture is too large
        """
        profile_picture = self.cleaned_data.get('profile_picture')
        
        if profile_picture:
            # Check file size (5MB limit)
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB in bytes
                logger.warning(
                    f"User {self.instance.username} attempted to upload oversized profile picture",
                    extra={
                        'user_id': self.instance.id,
                        'username': self.instance.username,
                        'file_size': profile_picture.size,
                        'max_size': 5 * 1024 * 1024,
                        'action': 'profile_picture_upload_failed'
                    }
                )
                raise forms.ValidationError('Profile picture size should not exceed 5MB.')
                
        return profile_picture
        
    def save(self, commit: bool = True) -> Any:
        """
        Save the form data to the model instance.
        
        Args:
            commit: Whether to save the model instance to the database
            
        Returns:
            The saved user instance
        """
        user = self.instance
        
        # Track which fields were updated
        updated_fields = []
        
        # Compare with initial values to determine what changed
        if hasattr(self, 'initial_data'):
            if user.email != self.cleaned_data['email']:
                updated_fields.append('email')
                
            if user.first_name != self.cleaned_data['first_name']:
                updated_fields.append('first_name')
                
            if user.last_name != self.cleaned_data['last_name']:
                updated_fields.append('last_name')
                
            if user.bio != self.cleaned_data['bio']:
                updated_fields.append('bio')
        
        # Update the user instance with form data
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.bio = self.cleaned_data['bio']
        
        # Only update profile picture if a new one was provided
        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data['profile_picture']
            updated_fields.append('profile_picture')
            
        if commit:
            user.save()
            
            # Only log if fields were actually updated
            if updated_fields:
                # Log profile update
                logger.info(
                    f"User {user.username} updated profile fields: {', '.join(updated_fields)}",
                    extra={
                        'user_id': user.id,
                        'username': user.username,
                        'updated_fields': updated_fields,
                        'action': 'profile_update'
                    }
                )
                
                # Log user activity
                log_user_activity(
                    logger=logger,
                    user_id=user.id,
                    action="profile_updated",
                    details={
                        'updated_fields': updated_fields
                    }
                )
            
        return user
