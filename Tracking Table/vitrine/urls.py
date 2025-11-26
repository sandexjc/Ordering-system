from django.urls import path
from vitrine import views

app_name = 'vitrine'

urlpatterns = [
    path('create_vitrine/', views.CreateVitrine.as_view(), name='new_vitrine'),
    path('edit_vitrine/<int:pk>', views.EditVitrine.as_view(), name='edit_vitrine'),
    path('view_vitrine/<int:pk>', views.ViewVitrine.as_view(), name='vitrine_view'),
]