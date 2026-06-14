from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum, Avg, F
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import BoardGame, Publisher, Genre, Sale
from .forms import BoardGameForm
from .decorators import admin_required

def home_view(request):
    latest_games = BoardGame.objects.order_by('-created_at')[:1]
    
    popular_games = BoardGame.objects.annotate(
        sales_count=Count('sales')
    ).filter(
        sales_count__gt=0
    ).order_by('-sales_count')[:4]
    
    sale_games = BoardGame.objects.filter(
        price__lt=2000
    ).order_by('price')[:3]
    
    total_revenue = Sale.objects.aggregate(
        total=Sum(F('quantity') * F('unit_price'))
    )['total'] or 0
    
    top_publishers = Publisher.objects.annotate(
        games_count=Count('board_games')
    ).order_by('-games_count')[:3]
    
    games_in_stock = BoardGame.objects.filter(
        current_stock__gt=0
    ).count()
    
    context = {
        'latest_games': latest_games,
        'popular_games': popular_games,
        'sale_games': sale_games,
        'total_revenue': total_revenue,
        'top_publishers': top_publishers,
        'games_in_stock': games_in_stock,
    }
    return render(request, 'puzzlestore/home.html', context)

def catalog_view(request):
    games = BoardGame.objects.available()
    games = games.exclude(genres__name='Для вечеринок')
    games = games.order_by('-created_at', 'name')
    games = games.annotate(total_sales=Count('sales'))
    games = games.prefetch_related('genres', 'publisher')
    
    context = {'games': games}
    return render(request, 'puzzlestore/catalog.html', context)

def game_detail(request, pk):
    base_game = get_object_or_404(BoardGame, pk=pk)
    
    publisher_id = request.GET.get('publisher')
    
    if publisher_id:
        game = get_object_or_404(
            BoardGame.objects.select_related('publisher', 'age_limit'),
            name=base_game.name,
            publisher_id=publisher_id
        )
    else:
        game = get_object_or_404(
            BoardGame.objects.select_related('publisher', 'age_limit'),
            pk=pk
        )
    
    publishers = BoardGame.objects.filter(
        name=game.name
    ).select_related('publisher').order_by('price')
    
    sales = game.sales.select_related('user').all()
    creators = game.creators.all()
    genres = game.genres.all()
    
    context = {
        'game': game,
        'sales': sales,
        'creators': creators,
        'genres': genres,
        'publishers': publishers,
        'has_multiple_publishers': publishers.count() > 1,
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
    
    publishers_values = Publisher.objects.values('id', 'name', 'website')
    game_names_flat = BoardGame.objects.values_list('name', flat=True)[:10]
    game_prices_list = BoardGame.objects.values_list('name', 'price')[:10]
    
    games_in_stock_count = BoardGame.objects.filter(current_stock__gt=0).count()
    has_out_of_stock_games = BoardGame.objects.filter(current_stock=0).exists()
    
    update_message = ""
    delete_message = ""
    
    if request.method == 'POST':
        if 'action_update' in request.POST:
            count = Sale.objects.filter(status='new').update(status='paid')
            update_message = f"Метод update() сработал. Обновлено продаж: {count}"
            
        elif 'action_delete' in request.POST:
            count, _ = Sale.objects.filter(status='cancelled').delete()
            delete_message = f"Метод delete() сработал. Удалено записей: {count}"

    new_sales_count = Sale.objects.filter(status='new').count()
    cancelled_sales_count = Sale.objects.filter(status='cancelled').count()
    
    game_prices_list_updated = BoardGame.objects.values_list('name', 'price')[:10]
    
    context = {
        'publishers': publishers,
        'games_revenue': games_revenue,
        'genre_stats': genre_stats,
        'total_revenue': total_revenue,
        'publishers_values': publishers_values,
        'game_names_flat': game_names_flat,
        'game_prices_list': game_prices_list,
        'game_prices_list_updated': game_prices_list_updated,
        'games_in_stock_count': games_in_stock_count,
        'has_out_of_stock_games': has_out_of_stock_games,
        'new_sales_count': new_sales_count,
        'cancelled_sales_count': cancelled_sales_count,
        'update_message': update_message,
        'delete_message': delete_message,
    }
    return render(request, 'puzzlestore/stats.html', context)

@admin_required
def games_crud_view(request):
    games = BoardGame.objects.all().select_related('publisher', 'age_limit')
    highlight_id = request.GET.get('highlight')
    context = {
        'games': games,
        'highlight_id': highlight_id,
    }
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

@admin_required
def bulk_update_sales(request):
    if request.method == 'POST':
        updated_count = Sale.objects.filter(status='new').update(status='paid')
        messages.success(request, f'Обновлено продаж: {updated_count}')
        return redirect('puzzlestore:search')
    
    new_sales_count = Sale.objects.filter(status='new').count()
    context = {'new_sales_count': new_sales_count}
    return render(request, 'puzzlestore/bulk_update_confirm.html', context)

@admin_required
def bulk_delete_sales(request):
    if request.method == 'POST':
        deleted_count, deleted_info = Sale.objects.filter(status='cancelled').delete()
        messages.success(request, f'Удалено продаж: {deleted_count}')
        return redirect('puzzlestore:search')
    
    cancelled_sales_count = Sale.objects.filter(status='cancelled').count()
    context = {'cancelled_sales_count': cancelled_sales_count}
    return render(request, 'puzzlestore/bulk_delete_confirm.html', context)

def search_view(request):
    query = request.GET.get('q', '')
    genre_id = request.GET.get('genre', '')
    publisher_ids = request.GET.getlist('publisher')
    limit = int(request.GET.get('limit', 5))
    
    base_queryset = BoardGame.objects.select_related('publisher', 'age_limit')
    
    if query:
        base_queryset = base_queryset.filter(name__icontains=query)
    
    if genre_id:
        base_queryset = base_queryset.filter(genres__id=genre_id)
    
    if publisher_ids:
        base_queryset = base_queryset.filter(publisher__id__in=publisher_ids)
    
    total_count = base_queryset.count()
    
    results = base_queryset[:limit]
    
    has_more = total_count > limit
    next_limit = limit + 5
    
    publishers_values = Publisher.objects.values('id', 'name', 'website')
    
    genres_list = Genre.objects.all().order_by('name')
    
    context = {
        'query': query,
        'results': results,
        'total_count': total_count,
        'has_more': has_more,
        'next_limit': next_limit,
        'publishers_values': publishers_values,
        'genres_list': genres_list,
        'current_genre_id': int(genre_id) if genre_id else None,
        'current_publisher_ids': [int(p) for p in publisher_ids] if publisher_ids else [],
    }
    return render(request, 'puzzlestore/search.html', context)

def custom_404(request, exception):
    messages.warning(request, 'Запрашиваемая страница не найдена')
    return redirect('puzzlestore:catalog')