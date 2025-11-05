from django.urls import path
from vitrine.views import CreateOrder

app_name = 'vitrine'

urlpatterns = [
    path('create_order/', CreateOrder.as_view(), name='new_order'),
]