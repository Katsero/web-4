import random
from decimal import Decimal
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.utils import timezone
from faker import Faker
from puzzlestore.models import (
    BoardGame, Genre, Publisher, Creator, AgeLimit, User,
    Supply, Sale, Cart, Wishlist, BoardGameCreator
)

class Command(BaseCommand):
    help = 'Generate realistic test data for the store'

    def add_arguments(self, parser):
        parser.add_argument('--games', type=int, default=20, help='Number of games to generate')
        parser.add_argument('--users', type=int, default=5, help='Number of new users to generate')

    def _download_image(self, seed):
        try:
            import urllib.request
            url = f"https://picsum.photos/seed/{seed}/400/400"
            with urllib.request.urlopen(url, timeout=5) as response:
                image_data = response.read()
            return ContentFile(image_data, name=f'game_{seed}.jpg')
        except Exception:
            return None

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker('ru_RU')

        genres = list(Genre.objects.all())
        publishers = list(Publisher.objects.all())
        creators = list(Creator.objects.all())
        age_limits = list(AgeLimit.objects.all())

        if not all([genres, publishers, creators, age_limits]):
            self.stderr.write('Reference data is missing. Please run initial data migration first.')
            return

        existing_users = list(User.objects.all())
        new_users = []
        for _ in range(options['users']):
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name() + str(random.randint(1, 999))
            new_users.append(User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123'
            ))
        all_users = existing_users + new_users

        game_names = [
            'Каркассон', 'Колонизаторы', 'Монополия', 'Уно', 'Манчкин',
            'Билет на поезд', 'Пандемия', 'Кодовые имена', 'Имаджинариум',
            'Экивоки', 'Взрывные котята', 'Тик так бумм', 'Свинтус',
            'Дженга', 'Эрудит', 'Башня', 'Мафия', 'Бункер', 'Техас',
            'Соображарий', 'Холм', 'Берсерк', 'Гвинт', 'Ведьмак',
            '7 чудес', 'Диксит', 'Активити', 'Крокодил',
            'Элиас', 'Время Валеры', 'Зомби в доме',
            'Подземелье', 'Драконья гавань', 'Терраформирование',
            'Барабашка', 'Доббль', 'Цитадели',
            'Санкт-Петербург', 'Пуэрто-Рико', 'Агрикола',
            'Ужас Аркхэма', 'Немезис', 'Сквозь века'
        ]

        games = []
        created_count = 0
        skipped_count = 0

        for i in range(options['games']):
            if i < len(game_names):
                name = game_names[i]
            else:
                name = f"{fake.word().title()} {fake.word().title()} {i}"

            publisher = random.choice(publishers)

            if BoardGame.objects.filter(name=name, publisher=publisher).exists():
                skipped_count += 1
                continue

            game = BoardGame(
                name=name,
                description=fake.paragraph(nb_sentences=4),
                price=Decimal(str(round(random.uniform(800, 4500), 2))),
                publisher=publisher,
                age_limit=random.choice(age_limits),
                current_stock=random.randint(0, 60),
                rating_avg=Decimal(str(round(random.uniform(3.5, 5.0), 2))) if random.random() > 0.2 else None,
            )

            image_file = self._download_image(f'{name}_{i}')
            if image_file:
                game.image = image_file

            try:
                game.save()
            except IntegrityError:
                skipped_count += 1
                continue

            k_genres = min(random.randint(1, 3), len(genres))
            game.genres.set(random.sample(genres, k=k_genres))

            k_creators = min(random.randint(1, 2), len(creators))
            selected_creators = random.sample(creators, k=k_creators)
            for cr in selected_creators:
                BoardGameCreator.objects.get_or_create(game=game, creator=cr)

            games.append(game)
            created_count += 1

        for game in games:
            supply_date = fake.date_between(start_date='-1y', end_date='-2m')
            Supply.objects.create(
                game=game,
                quantity=random.randint(20, 100),
                unit_cost=Decimal(str(round(float(game.price) * random.uniform(0.5, 0.7), 2))),
                supply_date=supply_date
            )

            if random.random() > 0.3:
                Sale.objects.create(
                    game=game,
                    quantity=random.randint(1, 4),
                    unit_price=game.price,
                    sale_date=timezone.make_aware(fake.date_time_between(start_date='-6m', end_date='now')),
                    user=random.choice(all_users) if random.random() > 0.4 and all_users else None,
                    status=random.choice(['new', 'paid', 'shipped', 'delivered', 'cancelled'])
                )

        active_users = all_users[:min(5, len(all_users))]
        for user in active_users:
            k_cart = min(random.randint(1, 3), len(games))
            if k_cart > 0:
                cart_games = random.sample(games, k=k_cart)
                for g in cart_games:
                    Cart.objects.get_or_create(user=user, game=g, defaults={'quantity': random.randint(1, 2)})

                remaining_games = [g for g in games if g not in cart_games]
                if remaining_games:
                    k_wish = min(random.randint(1, 2), len(remaining_games))
                    wish_games = random.sample(remaining_games, k=k_wish)
                    for g in wish_games:
                        Wishlist.objects.get_or_create(user=user, game=g)

        self.stdout.write(self.style.SUCCESS(
            f'Generated: {created_count} games, {len(new_users)} new users, supplies, sales, carts and wishlists. Skipped: {skipped_count} (duplicates).'
        ))