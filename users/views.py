from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import CustomUser
from django.views.generic import DetailView

from interaction.models import Favorite
from catalog.models import AITool 
from catalog.views import get_recommended_tools
import posthog # Import PostHog
from django.conf import settings # Import Django settings
from django.contrib.auth import login # To log in the user after registration


class RegisterView(CreateView):
    """
    View for registering new users.
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login') # Or 'catalog:home' if you want to redirect to home
    
    def form_valid(self, form):
        # Save the new user
        response = super().form_valid(form)
        new_user = self.object # The newly created user instance

        # Log the user in
        login(self.request, new_user)
        messages.success(self.request, _(f'Welcome, {new_user.username}! Your account has been created and you are now logged in.'))
        
        # PostHog: Identify the user and capture user_registered event
        if settings.POSTHOG_API_KEY:
            # Identify the user in PostHog. This creates/updates their profile.
            posthog.identify(
                new_user.email, # Using email as the distinct_id
                properties={
                    'username': new_user.username,
                    'email': new_user.email,
                    # Add any other user properties you want to store on their PostHog profile
                    # e.g., 'date_joined': new_user.date_joined.isoformat()
                }
            )
            
            # Capture the user_registered event
            posthog.capture(
                new_user.email, # Distinct ID
                'user_registered',
                properties={
                    # You can add properties specific to the registration event if needed
                    # For example, 'registration_method': 'direct_form'
                }
            )
            
        return response # Return the original response (usually a redirect)


class CustomLoginView(LoginView):
    """
    Custom login view that uses email instead of username.
    """
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, _('Invalid login. Please check your email and password.'))
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    """
    View for displaying user profile without editing.
    """
    model = CustomUser
    template_name = 'users/profile.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = Favorite.objects.filter(user=self.request.user)
        
        recommended_tools = get_recommended_tools(self.request.user)
        context['recommended_tools'] = recommended_tools
        
        from interaction.models import Conversation
        context['conversations'] = Conversation.objects.filter(user=self.request.user).order_by('-updated_at')[:5]
        
        return context
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Allows a logged-in user to change their password.
    """
    form_class = PasswordChangeForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:profile')  # O donde quieras redirigir

    def form_valid(self, form):
        messages.success(self.request, _('Your password was successfully updated!'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Please correct the error below.'))
        return super().form_invalid(form)
