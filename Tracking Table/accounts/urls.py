from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('createUser/', views.CreateUser.as_view(), name='createUser'),
    path('viewUsers/', views.ViewUsers.as_view(), name='viewUsers'),
]