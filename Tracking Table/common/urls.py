""" Ordering system URL Configuration """

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from common.views import Internals, Externals

urlpatterns = [
    # Site resources
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='internals/'), name='home'),
    path('internals/', Internals.InternalsView.as_view(), name='internals'),
    path('externals/', Externals.ExternalsView.as_view(), name='externals'),

    # Accounts app resources
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Table app resources
    path('table/', include('table.urls', namespace='table')),
]
