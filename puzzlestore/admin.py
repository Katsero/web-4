from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
import os
from .models import (
    Role, AgeLimit, Publisher, Genre, Creator, Profile,
    BoardGame, BoardGameCreator,
    Supply, Sale, Cart, Wishlist
)
import csv
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

UBUNTU_REGULAR = 'Ubuntu-Regular'
UBUNTU_BOLD = 'Ubuntu-Bold'

try:
    fonts_path = os.path.join(settings.BASE_DIR, 'puzzlestore', 'static', 'puzzlestore', 'fonts', 'Ubuntu')
    pdfmetrics.registerFont(TTFont(UBUNTU_REGULAR, os.path.join(fonts_path, 'Ubuntu-Regular.ttf')))
    pdfmetrics.registerFont(TTFont(UBUNTU_BOLD, os.path.join(fonts_path, 'Ubuntu-Bold.ttf')))
except:
    pass

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
    list_display = ('id', 'name', 'website',)
    list_display_links = ('name',)
    search_fields = ('name', 'website',)

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

    actions = ['export_supplies_to_pdf']

    @admin.action(description='Экспорт выбранных поставок в PDF')
    def export_supplies_to_pdf(self, request, queryset):
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Normal'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor('#0367A6'),
            fontName=UBUNTU_BOLD
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.grey,
            fontName=UBUNTU_REGULAR
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            fontName=UBUNTU_REGULAR
        )
        
        elements = []
        
        elements.append(Paragraph("Отчёт по поставкам", title_style))
        elements.append(Paragraph(
            f"Дата формирования: {timezone.now().strftime('%d.%m.%Y %H:%M')}",
            subtitle_style
        ))
        elements.append(Paragraph(
            f"Выбрано поставок: {queryset.count()}",
            subtitle_style
        ))
        elements.append(Spacer(1, 0.5*cm))
        
        table_data = [[
            Paragraph('<b>ID</b>', normal_style),
            Paragraph('<b>Игра</b>', normal_style),
            Paragraph('<b>Количество</b>', normal_style),
            Paragraph('<b>Себестоимость</b>', normal_style),
            Paragraph('<b>Сумма</b>', normal_style),
            Paragraph('<b>Дата поставки</b>', normal_style),
        ]]
        
        total_quantity = 0
        total_cost = 0
        
        for supply in queryset.select_related('game').order_by('supply_date'):
            total_sum = 0
            if supply.unit_cost:
                total_sum = supply.quantity * supply.unit_cost
                total_cost += total_sum
            total_quantity += supply.quantity
            
            sum_str = f"{total_sum:.2f} ₽" if supply.unit_cost else "—"
            cost_str = f"{supply.unit_cost:.2f} ₽" if supply.unit_cost else "—"
            
            table_data.append([
                Paragraph(str(supply.id), normal_style),
                Paragraph(supply.game.name, normal_style),
                Paragraph(str(supply.quantity), normal_style),
                Paragraph(cost_str, normal_style),
                Paragraph(sum_str, normal_style),
                Paragraph(supply.supply_date.strftime('%d.%m.%Y'), normal_style),
            ])
        
        total_style = ParagraphStyle(
            'TotalStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName=UBUNTU_BOLD,
            textColor=colors.HexColor('#0367A6')
        )
        
        table_data.append([
            Paragraph('<b>ИТОГО:</b>', total_style),
            '',
            Paragraph(f'<b>{total_quantity}</b>', total_style),
            '',
            Paragraph(f'<b>{total_cost:.2f} ₽</b>', total_style),
            '',
        ])
        
        col_widths = [1.5*cm, 8*cm, 3*cm, 4*cm, 4*cm, 3.5*cm]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0367A6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (4, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (5, 0), (5, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), UBUNTU_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#FFF1E9')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#66CCFF')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#0367A6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0367A6')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#0367A6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.HexColor('#FFF1E9'), colors.white]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        elements.append(Spacer(1, 1*cm))
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_RIGHT,
            fontName=UBUNTU_REGULAR
        )
        elements.append(Paragraph(
            f"PuzzleStore • Сформировано: {timezone.now().strftime('%d.%m.%Y %H:%M:%S')}",
            footer_style
        ))
        
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"supplies_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        self.message_user(request, f'Экспортировано поставок: {queryset.count()}')
        return response

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
    
    actions = ['mark_as_delivered']
    
    @admin.action(description='Пометить выбранные продажи как "Доставлено"')
    def mark_as_delivered(self, request, queryset):
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