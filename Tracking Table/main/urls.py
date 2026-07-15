""" Ordering system URL Configuration """

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from main.views import TableOrders, VitrineOrders

urlpatterns = [
    # Site resources
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="table/"), name="home"),
    path("table/", TableOrders.as_view(), name="table"),
    path("vitrine/", VitrineOrders.as_view(), name="vitrine"),

    # Accounts app resources
    path("accounts/", include("accounts.urls", namespace="accounts")),

    # Table app resources
    path("table/", include("table.urls", namespace="table")),

    # Vitrine app resources
    path("vitrine/", include("vitrine.urls", namespace="vitrine")),
]
