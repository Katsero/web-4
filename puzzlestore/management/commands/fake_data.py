import random
from django.core.management.base import BaseCommand
from django.db import transaction
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
        needed_users = max(0, options['users'] - len(existing_users))
        new_users = []
        for _ in range(needed_users):
            new_users.append(User.objects.create_user(
                username=fake.user_name(),
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
            '7 чудес', 'Имаджинариум', 'Диксит', 'Активити', 'Крокодил',
            'Элиас', 'Скажи иначе', 'Время Валеры', 'Зомби в доме',
            'Подземелье', 'Драконья гавань', 'Мачу-Пикчу', 'Терраформирование',
            'Гага', 'Барабашка', 'Доббль', 'Халифат', 'Цитадели',
            'Санкт-Петербург', 'Пуэрто-Рико', 'Агрикола', 'Каверна',
            'Ужас Аркхэма', 'Зов Ктулху', 'Немезис', 'Сквозь века'
        ]

        games = []
        used_names = set()

        for i in range(options['games']):
            if i < len(game_names):
                name = game_names[i]
            else:
                name = f"{fake.word().title()} {fake.word().title()} {i}"
            
            used_names.add(name)
            
            game = BoardGame.objects.create(
                name=name,
                image_url=f"https://picsum.photos/seed/{i}/400/400",
                description=fake.paragraph(nb_sentences=4),
                price=fake.pyfloat(min_value=800, max_value=4500, right_digits=2),
                publisher=random.choice(publishers),
                age_limit=random.choice(age_limits),
                current_stock=random.randint(0, 60),
                rating_avg=round(random.uniform(3.5, 5.0), 1) if random.random() > 0.2 else None,
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            game.genres.set(random.sample(genres, k=random.randint(1, 3)))

            selected_creators = random.sample(creators, k=random.randint(1, 2))
            for cr in selected_creators:
                BoardGameCreator.objects.create(game=game, creator=cr)

            games.append(game)

        for game in games:
            supply_date = fake.date_between(start_date='-1y', end_date='-2m')
            Supply.objects.create(
                game=game,
                quantity=random.randint(20, 100),
                unit_cost=game.price * random.uniform(0.5, 0.7),
                supply_date=supply_date
            )

            if random.random() > 0.3:
                Sale.objects.create(
                    game=game,
                    quantity=random.randint(1, 4),
                    unit_price=game.price,
                    sale_date=fake.date_time_between(start_date='-6m', end_date='now'),
                    user=random.choice(all_users) if random.random() > 0.4 else None
                )

        active_users = all_users[:min(5, len(all_users))]
        for user in active_users:
            cart_games = random.sample(games, k=random.randint(1, 3))
            for g in cart_games:
                Cart.objects.create(user=user, game=g, quantity=random.randint(1, 2))

            remaining_games = [g for g in games if g not in cart_games]
            if remaining_games:
                wish_games = random.sample(remaining_games, k=random.randint(1, 2))
                for g in wish_games:
                    Wishlist.objects.create(user=user, game=g)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully generated: {len(games)} games, {len(new_users)} users, '
            f'supplies, sales, carts and wishlists.'
        ))