from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import (
    Role, AgeLimit, Publisher, Genre, Creator, Profile,
    BoardGame, BoardGameCreator,
    Supply, Sale, Cart, Wishlist
)
import csv

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    readonly_fields = ('created_at',)

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    @admin.display(description='Роль', ordering='profile__role__name')
    def get_user_role(self, obj):
        return obj.profile.role.name if hasattr(obj, 'profile') and obj.profile.role else "—"
    get_user_role.short_description = 'Роль'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class BoardGameCreatorInline(admin.TabularInline):
    model = BoardGameCreator
    extra = 1
    raw_id_fields = ('creator',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)

@admin.register(AgeLimit)
class AgeLimitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('value',)

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)

@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role')
    list_display_links = ('name',)
    search_fields = ('name', 'role')
    list_filter = ('role',)

@admin.register(BoardGame)
class BoardGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'publisher', 'price', 'current_stock', 'get_rating_status', 'created_at')
    list_display_links = ('name',)
    list_filter = ('publisher', 'age_limit', 'genres', 'created_at')
    search_fields = ('name', 'description', 'genres__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('current_stock', 'created_at', 'rating_avg')
    
    filter_horizontal = ('genres',)
    inlines = [BoardGameCreatorInline]
    
    actions = ['export_to_csv']
    
    @admin.action(description='Экспорт выбранных игр в CSV')
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="games_export.csv"'

        response.write('\ufeff')
        
        writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_ALL)
        
        writer.writerow([
            'ID',
            'Название',
            'Издатель',
            'Цена',
            'Остаток',
            'Рейтинг',
            'Дата добавления'
        ])
        
        for game in queryset.select_related('publisher'):
            rating = f"{game.rating_avg}" if game.rating_avg else "Нет оценок"
            writer.writerow([
                game.id,
                game.name,
                game.publisher.name,
                game.price,
                game.current_stock,
                rating,
                game.created_at.strftime('%d.%m.%Y')
            ])
        
        self.message_user(request, f'Экспортировано игр: {queryset.count()}')
        return response

    @admin.display(description='Статус рейтинга', ordering='rating_avg')
    def get_rating_status(self, obj):
        if obj.rating_avg:
            return f"{obj.rating_avg} ★"
        return "Нет оценок"
    get_rating_status.short_description = 'Рейтинг'

@admin.register(BoardGameCreator)
class BoardGameCreatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'creator')
    raw_id_fields = ('game', 'creator')

@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'quantity', 'unit_cost', 'get_total_cost', 'supply_date', 'created_at')
    list_display_links = ('game',)
    list_filter = ('game', 'supply_date')
    search_fields = ('game__name',)
    date_hierarchy = 'supply_date'
    raw_id_fields = ('game',)
    readonly_fields = ('created_at',)

    @admin.display(description='Сумма')
    def get_total_cost(self, obj):
        return f"{obj.quantity * obj.unit_cost} ₽" if obj.unit_cost else "—"

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'quantity', 'unit_price', 'get_total_price', 'sale_date', 'status', 'get_user_info')
    list_display_links = ('game',)
    list_filter = ('game', 'sale_date', 'user', 'status')
    search_fields = ('game__name', 'user__username', 'user__email')
    date_hierarchy = 'sale_date'
    raw_id_fields = ('game', 'user')
    readonly_fields = ('sale_date',)
    
    # ===== ДЕЙСТВИЕ: ПОМЕТИТЬ КАК ДОСТАВЛЕННО =====
    actions = ['mark_as_delivered']
    
    @admin.action(description='Пометить выбранные продажи как "Доставлено"')
    def mark_as_delivered(self, request, queryset):
        """Массово меняет статус продаж на 'delivered'"""
        updated = queryset.update(status='delivered')
        self.message_user(request, f'Обновлено продаж: {updated}')

    @admin.display(description='Итого')
    def get_total_price(self, obj):
        return f"{obj.quantity * obj.unit_price} ₽"

    @admin.display(description='Клиент')
    def get_user_info(self, obj):
        return f"{obj.user.username} ({obj.user.email})" if obj.user else "Гость/Не указан"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game', 'quantity', 'created_at')
    list_display_links = ('user', 'game')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'game__name')
    raw_id_fields = ('user', 'game')
    readonly_fields = ('created_at',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game', 'created_at')
    list_display_links = ('user', 'game')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'game__name')
    raw_id_fields = ('user', 'game')
    readonly_fields = ('created_at',)