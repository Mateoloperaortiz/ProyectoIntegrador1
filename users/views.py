from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import CustomUser
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


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    View for displaying and updating user profile.
    """
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _('Your profile has been updated!'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = Favorite.objects.filter(user=self.request.user)
        return context
