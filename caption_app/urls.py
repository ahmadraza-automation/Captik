from django.urls import path
from .views import dashboard_view, font_search_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('fonts/search/', font_search_view, name='font_search'),
]
