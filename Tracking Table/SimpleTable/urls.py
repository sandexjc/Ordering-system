""" SimpleTable URL Configuration """

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from SimpleTable import views

urlpatterns = [
    # Site resources
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='internals/'), name='home'),
    path('internals/', views.Internals.as_view(), name='internals'),
    path('externals/', views.Externals.as_view(), name='externals'),
    path('viewOrder/<int:pk>', views.OrderView.as_view(), name='order_view'),

    # Accounts app resources
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Table app resources
    path('table/', include('table.urls', namespace='table')),
]
