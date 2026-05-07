from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum, Avg, F
from .models import BoardGame, Publisher, Genre, Sale

def catalog_view(request):
    games = BoardGame.objects.filter(current_stock__gt=0)
    
    games = games.exclude(genres__name='Для вечеринок')
    
    games = games.order_by('-created_at', 'name')
    
    games = games.annotate(
        total_sales=Count('sales')
    )
    
    context = {
        'games': games,
    }
    return render(request, 'puzzlestore/catalog.html', context)

def game_detail(request, slug):
    game = get_object_or_404(BoardGame, slug=slug)
    
    sales = game.sales.all()
    
    publisher_name = game.publisher.name
    
    context = {
        'game': game,
        'sales': sales,
        'publisher_name': publisher_name,
    }
    return render(request, 'puzzlestore/game_detail.html', context)

def stats_view(request):
    publishers = Publisher.objects.annotate(
        games_count=Count('board_games')
    ).order_by('-games_count')
    
    games_revenue = BoardGame.objects.annotate(
        revenue=Sum(F('sales__quantity') * F('sales__unit_price'))
    ).filter(revenue__isnull=False).order_by('-revenue')
    
    genre_stats = Genre.objects.annotate(
        avg_price=Avg('board_games__price'),
        games_count=Count('board_games')
    ).filter(games_count__gt=0)
    
    total_revenue = Sale.objects.aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total']
    
    context = {
        'publishers': publishers,
        'games_revenue': games_revenue,
        'genre_stats': genre_stats,
        'total_revenue': total_revenue,
    }
    return render(request, 'puzzlestore/stats.html', context)