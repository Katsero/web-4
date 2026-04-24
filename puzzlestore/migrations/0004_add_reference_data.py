from django.db import migrations

def add_reference_data(apps, schema_editor):
    Role = apps.get_model('puzzlestore', 'Role')
    AgeLimit = apps.get_model('puzzlestore', 'AgeLimit')
    Publisher = apps.get_model('puzzlestore', 'Publisher')
    Genre = apps.get_model('puzzlestore', 'Genre')
    Creator = apps.get_model('puzzlestore', 'Creator')

    roles_data = [
        {'name': 'Администратор'},
        {'name': 'Пользователь'},
    ]
    for role in roles_data:
        Role.objects.get_or_create(name=role['name'])

    ages_data = [
        {'name': '0+', 'value': 0},
        {'name': '6+', 'value': 6},
        {'name': '12+', 'value': 12},
        {'name': '16+', 'value': 16},
        {'name': '18+', 'value': 18},
    ]
    for age in ages_data:
        AgeLimit.objects.get_or_create(name=age['name'], defaults={'value': age['value']})

    publishers_data = [
        {'name': 'Hasbro'},
        {'name': 'Zvezda (Звезда)'},
        {'name': 'Lavka Games'},
        {'name': 'Hobby World'},
        {'name': 'GaGa Games'},
    ]
    for pub in publishers_data:
        Publisher.objects.get_or_create(name=pub['name'])

    genres_data = [
        {'name': 'Стратегия'},
        {'name': 'Для вечеринок'},
        {'name': 'Семейная'},
        {'name': 'Карточная'},
        {'name': 'Кооперативная'},
    ]
    for gen in genres_data:
        Genre.objects.get_or_create(name=gen['name'])

    creators_data = [
        {'name': 'Клаус Тойбер'},
        {'name': 'Райнер Книция'},
        {'name': 'Дмитрий Князев'},
        {'name': 'Сергей Мачин'},
        {'name': 'Фил Уокер-Хардинг'},
    ]
    for cr in creators_data:
        Creator.objects.get_or_create(name=cr['name'])

class Migration(migrations.Migration):
    dependencies = [
        ('puzzlestore', '0003_boardgame_genres_delete_boardgamegenre'), 
    ]

    operations = [
        migrations.RunPython(add_reference_data),
    ]