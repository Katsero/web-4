from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum, Avg, F
from .models import BoardGame, Publisher, Genre, Sale

def catalog_view(request):
    games = BoardGame.objects.available()
    games = games.exclude(genres__name='Для вечеринок')
    games = games.order_by('-created_at', 'name')
    games = games.annotate(total_sales=Count('sales'))
    
    games = games.prefetch_related('genres', 'publisher')
    
    context = {'games': games}
    return render(request, 'puzzlestore/catalog.html', context)

def game_detail(request, pk):
    game = get_object_or_404(
        BoardGame.objects.select_related('publisher', 'age_limit'),
        pk=pk
    )
    
    sales = game.sales.select_related('user').all()
    creators = game.creators.all()
    genres = game.genres.all()
    
    context = {
        'game': game,
        'sales': sales,
        'creators': creators,
        'genres': genres,
    }
    return render(request, 'puzzlestore/game_detail.html', context)

def stats_view(request):
    publishers = Publisher.objects.annotate(
        games_count=Count('board_games')
    ).order_by('-games_count').prefetch_related('board_games')
    
    games_revenue = BoardGame.objects.select_related('publisher').annotate(
        revenue=Sum(F('sales__quantity') * F('sales__unit_price'))
    ).filter(revenue__isnull=False).order_by('-revenue')
    
    genre_stats = Genre.objects.annotate(
        avg_price=Avg('board_games__price'),
        games_count=Count('board_games')
    ).filter(games_count__gt=0).prefetch_related('board_games')
    
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