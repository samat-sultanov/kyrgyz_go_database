from django.urls import path
from django.contrib.auth import views as auth_views

from django.contrib.auth.views import LoginView, LogoutView
from accounts.views import UserDetailView, UserChangeView

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<int:pk>/', UserDetailView.as_view(), name='detail'),
    path('change/',  UserChangeView.as_view(), name='change'),

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
]
