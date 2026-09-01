from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('change-password/', views.ChangePassword.as_view(), name='change-password'),
    path('create-user/', views.CreateUser.as_view(), name='create-user'),
    path('view-users/', views.ViewUsers.as_view(), name='view-users'),
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
    path(
        'set-password/<uidb64>/<token>/',
        views.SetNewPassword.as_view(),
        name='set-password',
    ),
]