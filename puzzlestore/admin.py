from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Role, AgeLimit, Publisher, Genre, Creator, Profile,
    BoardGame, BoardGameCreator,
    Supply, Sale, Cart, Wishlist
    )

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

## старое
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'username', 'email', 'phone', 'get_role_display', 'created_at')
#     list_display_links = ('username',)
#     list_filter = ('role', 'created_at')
#     search_fields = ('username', 'email', 'phone')
#     date_hierarchy = 'created_at'
#     readonly_fields = ('created_at',)

#     @admin.display(description='Роль', ordering='role__name')
#     def get_role_display(self, obj):
#         return obj.role.name
#     get_role_display.short_description = 'Роль'

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