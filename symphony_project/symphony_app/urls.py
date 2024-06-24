# symphony_app/urls.py
from django.urls import path
from .views import save_entity, get_entity

urlpatterns = [
    path('api/save-entity/', save_entity, name='save_entity'),
    path('api/get-entity/', get_entity, name='get_entity'),
]
