from django.contrib import admin
from .models import (
    Role, AgeLimit, Publisher, Genre, Creator,
    User, BoardGame, BoardGameGenre, BoardGameCreator,
    Supply, Sale, Cart, Wishlist
)

class BoardGameGenreInline(admin.TabularInline):
    model = BoardGameGenre
    extra = 1
    raw_id_fields = ('genre',)

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

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'get_role_display', 'created_at')
    list_display_links = ('username',)
    list_filter = ('role', 'created_at')
    search_fields = ('username', 'email', 'phone')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    @admin.display(description='Роль', ordering='role__name')
    def get_role_display(self, obj):
        return obj.role.name
    get_role_display.short_description = 'Роль'

@admin.register(BoardGame)
class BoardGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'publisher', 'price', 'current_stock', 'get_rating_status', 'created_at')
    list_display_links = ('name',)
    list_filter = ('publisher', 'age_limit', 'created_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'rating_avg')
    inlines = [BoardGameGenreInline, BoardGameCreatorInline]

    @admin.display(description='Статус рейтинга', ordering='rating_avg')
    def get_rating_status(self, obj):
        if obj.rating_avg:
            return f"{obj.rating_avg} ★"
        return "Нет оценок"
    get_rating_status.short_description = 'Рейтинг'

@admin.register(BoardGameGenre)
class BoardGameGenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'genre')
    raw_id_fields = ('game', 'genre')

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

    @admin.display(description='Общая стоимость')
    def get_total_cost(self, obj):
        return f"{obj.quantity * obj.unit_cost} ₽" if obj.unit_cost else "—"
    get_total_cost.short_description = 'Сумма'

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'quantity', 'unit_price', 'get_total_price', 'sale_date', 'get_user_info')
    list_display_links = ('game',)
    list_filter = ('game', 'sale_date', 'user')
    search_fields = ('game__name', 'user__username', 'user__email')
    date_hierarchy = 'sale_date'
    raw_id_fields = ('game', 'user')
    readonly_fields = ('sale_date',)

    @admin.display(description='Сумма продажи')
    def get_total_price(self, obj):
        return f"{obj.quantity * obj.unit_price} ₽"
    get_total_price.short_description = 'Итого'

    @admin.display(description='Покупатель')
    def get_user_info(self, obj):
        return f"{obj.user.username} ({obj.user.email})" if obj.user else "Гость/Не указан"
    get_user_info.short_description = 'Клиент'

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