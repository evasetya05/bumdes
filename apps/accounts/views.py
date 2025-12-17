from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.forms import AuthenticationForm

class LoginView(BaseLoginView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/dashboard/'  # Update this to your dashboard URL

def login_view(request):
    return LoginView.as_view()(request)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
