from django.db import models
from django.utils import timezone

class Role(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Название роли"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        ordering = ['name']

    def __str__(self):
        return self.name

class AgeLimit(models.Model):
    name = models.CharField(
        max_length=10,
        verbose_name="Название ограничения"
    )
    value = models.PositiveSmallIntegerField(
        verbose_name="Минимальный возраст"
    )

    class Meta:
        verbose_name = "Возрастное ограничение"
        verbose_name_plural = "Возрастные ограничения"
        ordering = ['value']

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название издателя"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Страна"
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name="Сайт"
    )

    class Meta:
        verbose_name = "Издатель"
        verbose_name_plural = "Издатели"
        ordering = ['name']

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название жанра"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание жанра"
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']

    def __str__(self):
        return self.name


class Creator(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Имя создателя"
    )
    role = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Роль (дизайнер/художник и т.д.)"
    )

    class Meta:
        verbose_name = "Создатель"
        verbose_name_plural = "Создатели"
        ordering = ['name']

    def __str__(self):
        return self.name

class User(models.Model):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Имя пользователя"
    )
    password_hash = models.CharField(
        max_length=255,
        verbose_name="Хэш пароля"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон"
    )
    avatar_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на аватар"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name="Роль"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.email})"

class BoardGame(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название игры"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="URL-слаг"
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на изображение"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    age_limit = models.ForeignKey(
        AgeLimit,
        on_delete=models.PROTECT,
        related_name='board_games',
        verbose_name="Возрастное ограничение"
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.PROTECT,
        related_name='board_games',
        verbose_name="Издатель"
    )
    current_stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Текущий остаток на складе"
    )
    rating_avg = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Средний рейтинг"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    class Meta:
        verbose_name = "Настольная игра"
        verbose_name_plural = "Настольные игры"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class BoardGameGenre(models.Model):
    game = models.ForeignKey(
        BoardGame,
        on_delete=models.CASCADE,
        related_name='genres',
        verbose_name="Игра"
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='games',
        verbose_name="Жанр"
    )

    class Meta:
        verbose_name = "Жанр игры"
        verbose_name_plural = "Жанры игр"
        unique_together = ['game', 'genre']
        ordering = ['game', 'genre']

    def __str__(self):
        return f"{self.game} - {self.genre}"

class BoardGameCreator(models.Model):
    game = models.ForeignKey(
        BoardGame,
        on_delete=models.CASCADE,
        related_name='creators',
        verbose_name="Игра"
    )
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name='games',
        verbose_name="Создатель"
    )

    class Meta:
        verbose_name = "Создатель игры"
        verbose_name_plural = "Создатели игр"
        unique_together = ['game', 'creator']
        ordering = ['game', 'creator']

    def __str__(self):
        return f"{self.game} - {self.creator}"

class Supply(models.Model):
    game = models.ForeignKey(
        BoardGame,
        on_delete=models.PROTECT,
        related_name='supplies',
        verbose_name="Игра"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество"
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Себестоимость за единицу"
    )
    supply_date = models.DateField(
        default=timezone.now,
        verbose_name="Дата поставки"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата записи"
    )

    class Meta:
        verbose_name = "Поставка"
        verbose_name_plural = "Поставки"
        ordering = ['-supply_date']

    def __str__(self):
        return f"{self.game} - {self.quantity} шт. ({self.supply_date})"


class Sale(models.Model):
    game = models.ForeignKey(
        BoardGame,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name="Игра"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена продажи за единицу"
    )
    sale_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата продажи"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='purchases',
        verbose_name="Покупатель"
    )

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"
        ordering = ['-sale_date']

    def __str__(self):
        return f"{self.game} - {self.quantity} шт. на {self.unit_price * self.quantity} ₽ ({self.sale_date})"

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name="Пользователь"
    )
    game = models.ForeignKey(
        BoardGame,
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name="Игра"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Корзины"
        unique_together = ['user', 'game']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.game} ({self.quantity} шт.)"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name="Пользователь"
    )
    game = models.ForeignKey(
        BoardGame,
        on_delete=models.CASCADE,
        related_name='in_wishlists',
        verbose_name="Игра"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Желаемое количество"
    )
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name="Заметка"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )

    class Meta:
        verbose_name = "Товар в желаемом"
        verbose_name_plural = "Желаемое"
        unique_together = ['user', 'game']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} хочет {self.game}"