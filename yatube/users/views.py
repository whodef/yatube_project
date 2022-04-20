from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordChangeView

from .forms import CreationForm


class SignUp(CreateView):
    """Когда юзер зарегистировался, переход на главную."""
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class CustomLoginView(LoginView):
    """Страница входа в аккаунт."""
    template_name = "users/login.html"


class CustomLogoutView(LogoutView):
    """Страница выхода из аккаунта."""
    template_name = "users/logged_out.html"


class CustomPasswordResetView(PasswordResetView):
    """При сбросе пароля."""
    success_url = reverse_lazy("users:password_reset_done")
    email_template_name = "users/password_reset_email.html"
    template_name = "users/password_reset_form.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Страница сброса пароля."""
    success_url = reverse_lazy("users:password_reset_complete")
    template_name = "users/password_reset_confirm.html"


class CustomPasswordChangeView(PasswordChangeView):
    """Страница подтверждения сброса пароля."""
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
