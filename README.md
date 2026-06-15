python -m venv .venv  
pip install django
django-admin startproject web . 
python manage.py startapp puzzlestore
python manage.py createsuperuser
    Kat
    1234
python manage.py runserver
pip freeze > requirements.txt
pip freeze | Out-File -Encoding utf8 requirements.txt
    если кодировка шакалит
pip install -r requirements.txt
docker-compose up -d