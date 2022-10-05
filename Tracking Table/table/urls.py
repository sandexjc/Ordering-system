from django.urls import path
from table import views

app_name = 'table'

urlpatterns = [
    path('createOrder/', views.CreateOrder.as_view(), name='newOrder'),
    path('editOrder/<int:pk>/', views.EditOrder.as_view(), name='editOrder'),
    path('deleteOrder/<int:pk>', views.DeleteOrder.as_view(), name='deleteOrder'),
    path('updateOrder/<int:pk>', views.UpdateOrder.as_view(), name='updateOrder'),
    path('printOrder/<int:pk>', views.PrintOrder.as_view(), name='printOrder'),
    path('getOrderHistory/<int:pk>', views.GetOrderHistory.as_view(), name='orderHistory'),
]