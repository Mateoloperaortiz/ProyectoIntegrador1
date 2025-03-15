from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user in the registration process.
    """
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text=_('Required. Enter a valid email address.'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    
    username = forms.CharField(
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    
    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        help_text=_('Enter the same password as before, for verification.')
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """
    Form for logging in users with email and password.
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'bio', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }