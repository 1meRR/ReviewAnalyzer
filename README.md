установить зависимости: pip install -r requirements.txt (django, djangorestframework, textblob, nltk, matplotlib)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

открыть http://127.0.0.1:8000/

api:
GET /api/reviews/
POST /api/reviews/
GET /api/analysis/
GET /api/analysis/summary/
POST /api/login/
POST /api/users/
