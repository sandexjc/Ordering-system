from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('create-user/', views.CreateUser.as_view(), name='create-user'),
    path('view-users/', views.ViewUsers.as_view(), name='view-users'),
    path(
        'view-users/<int:pk>/send-set-password-email/',
        views.SendSetPasswordEmail.as_view(),
        name='send-set-password-email',
    ),
    path(
        'set-password/<uidb64>/<token>/',
        views.SetPassword.as_view(),
        name='set-password',
    ),
]