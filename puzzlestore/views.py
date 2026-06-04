from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum, Avg, F
from django.contrib import messages
from .models import BoardGame, Publisher, Genre, Sale
from .forms import BoardGameForm
from .decorators import admin_required

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

@admin_required
def games_crud_view(request):
    games = BoardGame.objects.all().select_related('publisher', 'age_limit')
    context = {'games': games}
    return render(request, 'puzzlestore/games.html', context)

@admin_required
def game_create(request):
    if request.method == 'POST':
        form = BoardGameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Игра успешно добавлена')
            return redirect('puzzlestore:games_crud')
    else:
        form = BoardGameForm()
    
    context = {'form': form, 'title': 'Добавить игру'}
    return render(request, 'puzzlestore/game_form.html', context)

@admin_required
def game_update(request, pk):
    game = get_object_or_404(BoardGame, pk=pk)
    
    if request.method == 'POST':
        form = BoardGameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, 'Игра успешно обновлена')
            return redirect('puzzlestore:games_crud')
    else:
        form = BoardGameForm(instance=game)
    
    context = {'form': form, 'title': f'Редактировать: {game.name}'}
    return render(request, 'puzzlestore/game_form.html', context)

@admin_required
def game_delete(request, pk):
    game = get_object_or_404(BoardGame, pk=pk)
    
    if request.method == 'POST':
        game.delete()
        messages.success(request, 'Игра успешно удалена')
        return redirect('puzzlestore:games_crud')
    
    context = {'game': game}
    return render(request, 'puzzlestore/game_confirm_delete.html', context)


def custom_404(request, exception):
    messages.warning(request, 'Запрашиваемая страница не найдена')
    return redirect('puzzlestore:catalog')