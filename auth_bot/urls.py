from django.urls import path
from .views import bale_webhook_view

urlpatterns = [
    path('bale-webhook/', bale_webhook_view, name='bale_webhook'),
]