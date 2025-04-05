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

class RegisterView(CreateView):
    """
    View for registering new users.
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        messages.success(self.request, _('Your account has been created! You can now log in.'))
        return super().form_valid(form)


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