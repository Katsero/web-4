from django.urls import path
from . import views

app_name = 'puzzlestore'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('game/<slug:slug>/', views.game_detail, name='game_detail'),
]