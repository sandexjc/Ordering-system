""" Ordering system URL Configuration """

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from main.views import Orders, Offers

urlpatterns = [
    # Site resources
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='internals/'), name='home'),
    path('internals/', Orders.as_view(), name='internals'),
    path('externals/', Offers.as_view(), name='externals'),

    # Accounts app resources
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Table app resources
    path('table/', include('table.urls', namespace='table')),
]
