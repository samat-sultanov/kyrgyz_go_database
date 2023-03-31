from django.urls import path
from django.contrib.auth import views as auth_views

from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from accounts.views import UserDetailView

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<int:pk>/', UserDetailView.as_view(), name='detail'),

    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name='email_registration/password_reset.html',
        success_url='/accounts/reset_password_sent/'),
        name='reset_password'),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='email_registration/password_reset_sent.html',),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='email_registration/password_reset_form.html',
                                                     success_url='/accounts/reset_password_complete/'),
         name="password_reset_confirm"),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='email_registration/password_reset_done.html'),
         name="password_reset_complete"),
    path('change_password/',
         PasswordChangeView.as_view(template_name='email_registration/change_password.html',
                                    success_url='/accounts/change_password_done/'),
         name='change_password'),
]
