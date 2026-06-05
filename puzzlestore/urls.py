from django.urls import path
from . import views

app_name = 'puzzlestore'

urlpatterns = [
    path('', views.home_view, name='home'), 
    path('catalog/', views.catalog_view, name='catalog'),
    path('game/<int:pk>/', views.game_detail, name='game_detail'),
    path('stats/', views.stats_view, name='stats'),
    path('games/', views.games_crud_view, name='games_crud'),
    path('games/create/', views.game_create, name='game_create'),
    path('games/<int:pk>/update/', views.game_update, name='game_update'),
    path('games/<int:pk>/delete/', views.game_delete, name='game_delete'),
    path('search/', views.search_view, name='search'),
    path('search/bulk-update/', views.bulk_update_sales, name='bulk_update_sales'),
    path('search/bulk-delete/', views.bulk_delete_sales, name='bulk_delete_sales'),
]