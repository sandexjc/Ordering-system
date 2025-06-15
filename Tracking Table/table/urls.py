from django.urls import path
from table.views.CreateOrderView import CreateOrder
from table.views.DeleteOrderView import DeleteOrder
from table.views.OrderDetailsView import ViewOrder
from table.views.EditOrderView import EditOrder
from table.views.OrderHistoryView import OrderHistory
from table.views.PrintOrderView import PrintOrder
from table.views.UpdateOrderView import UpdateOrder

app_name = 'table'

urlpatterns = [
    path('createOrder/', CreateOrder.as_view(), name='newOrder'),
    path('editOrder/<int:pk>', EditOrder.as_view(), name='editOrder'),
    path('deleteOrder/<int:pk>', DeleteOrder.as_view(), name='deleteOrder'),
    path('updateOrder/<int:pk>', UpdateOrder.as_view(), name='updateOrder'),
    path('printOrder/<int:pk>', PrintOrder.as_view(), name='printOrder'),
    path('getOrderHistory/<int:pk>', OrderHistory.as_view(), name='orderHistory'),
    path('viewOrder/<int:pk>', ViewOrder.as_view(), name='order_view'),
]