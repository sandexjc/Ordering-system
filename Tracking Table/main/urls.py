""" Ordering system URL configuration """

from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from main.views import (
    DynamicView,
    DynamicTableOrdersData,
    DynamicVitrineOrdersData,
    TableOrders,
    VitrineOrders,
)


def home_redirect(request):
    if getattr(settings, "DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING", False):
        return redirect("dynamic")
    return redirect("table")

urlpatterns = [
    # Site resources
    path("", home_redirect, name="home"),
    path("admin/", admin.site.urls),
    path("table/", TableOrders.as_view(), name="table"),
    path("vitrine/", VitrineOrders.as_view(), name="vitrine"),
    path("dynamic/", DynamicView.as_view(), name="dynamic"),

    # Accounts app resources
    path("accounts/", include("accounts.urls", namespace="accounts")),

    # Table app resources
    path("table/", include("table.urls", namespace="table")),

    # Vitrine app resources
    path("vitrine/", include("vitrine.urls", namespace="vitrine")),

    # Dynamic content data endpoints
    path("dynamic/data/table/", DynamicTableOrdersData.as_view(), name="dynamic-table-orders"),
    path("dynamic/data/vitrine/", DynamicVitrineOrdersData.as_view(), name="dynamic-vitrine-orders"),
]
