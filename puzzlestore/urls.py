from django.urls import path
from . import views

app_name = 'puzzlestore'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('game/<int:pk>/', views.game_detail, name='game_detail'),
    path('stats/', views.stats_view, name='stats'),
]