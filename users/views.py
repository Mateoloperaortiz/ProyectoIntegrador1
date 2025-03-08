from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente después del registro
            return redirect('catalog:home')  # Redirige a home después del registro
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})  # 🔹 CORREGIDO

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('catalog:home')  # Redirige al home después de iniciar sesión
        else:
            return render(request, 'users/login.html', {'form': form, 'error': 'Invalid credentials'})  # 🔹 CORREGIDO
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})  # 🔹 CORREGIDO

def user_logout(request):
    logout(request)
    return redirect('catalog:home')  # Redirige al login después de cerrar sesión

@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})