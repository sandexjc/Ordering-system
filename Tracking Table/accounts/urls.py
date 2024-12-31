from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('create-user/', views.CreateUser.as_view(), name='create-user'),
    path('view-users/', views.ViewUsers.as_view(), name='view-users'),
]