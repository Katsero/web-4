python -m venv .venv  
pip install django
django-admin startproject web . 
python manage.py startapp puzzlestore
python manage.py createsuperuser
    Kat
    1234
python manage.py runserver

# работа с зависимостями
pip freeze > requirements.txt
pip freeze | Out-File -Encoding utf8 requirements.txt
    если кодировка шакалит
pip install -r requirements.txt


# postgre on docker init
docker-compose up -d
python manage.py migrate
## если контейнер крашится (вкл/выкл)
docker-compose down -v

# если надо запустить sql код
docker exec -it puzzlestore_db psql -U puzzlestore_user -d puzzlestore_db
    Вставить код