""" Ordering system URL Configuration """

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from main.views import Orders, Offers, Vitrines

urlpatterns = [
    # Site resources
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='internals/'), name='home'),
    path('internals/', Orders.as_view(), name='internals'),
    path('externals/', Offers.as_view(), name='externals'),
    path('vitrines/', Vitrines.as_view(), name='vitrines'),

    # Accounts app resources
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Table app resources
    path('table/', include('table.urls', namespace='table')),

    # Vitrine app resources
    path('vitrine/', include('vitrine.urls', namespace='vitrine'))
]
