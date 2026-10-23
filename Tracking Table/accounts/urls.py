from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    # Sign in and sign out.
    path(
        'login/',
        views.Login.as_view(),
        name='login',
    ),
    path(
        'logout/',
        views.Logout.as_view(),
        name='logout',
    ),

    # Logged-in profile and its device list.
    path(
        'profile/',
        views.Profile.as_view(),
        name='profile',
    ),
    path(
        'profile/devices/',
        views.DeviceList.as_view(),
        name='profile-devices',
    ),
    path(
        'profile/devices/send-activation-email/',
        views.DeviceActivationEmail.as_view(),
        name='send-device-activation-email',
    ),
    path(
        'profile/devices/<int:pk>/revoke/',
        views.RevokeDevice.as_view(),
        name='revoke-profile-device',
    ),

    # Password email for the logged-in user, and the public page that saves it.
    path(
        'change-password/',
        views.ChangePassword.as_view(),
        name='change-password',
    ),
    path(
        'set-password/<uidb64>/<token>/',
        views.SetNewPassword.as_view(),
        name='set-password',
    ),

    # Admin user management.
    path(
        'create-user/',
        views.CreateUser.as_view(),
        name='create-user',
    ),
    path(
        'view-users/',
        views.ViewUsers.as_view(),
        name='view-users',
    ),
    path(
        'view-users/<int:pk>/set-active/',
        views.SetUserActive.as_view(),
        name='set-user-active',
    ),
    path(
        'view-users/<int:pk>/set-role/',
        views.SetUserRole.as_view(),
        name='set-user-role',
    ),
    path(
        'view-users/<int:pk>/send-set-password-email/',
        views.AdminPasswordResetEmail.as_view(),
        name='send-set-password-email',
    ),

    # Public one-time link that enrolls a browser. Does not change the password.
    path(
        'activate-device/<uidb64>/<token>/',
        views.ActivateDevice.as_view(),
        name='activate-device',
    ),
]
