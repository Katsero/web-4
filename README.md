python -m venv .venv  
pip install django
pip freeze > requirements.txt
django-admin startproject web . 
python manage.py startapp puzzlestore
python manage.py createsuperuser
    Kat
    1234
python manage.py runserver
pip install -r requirements.txt 