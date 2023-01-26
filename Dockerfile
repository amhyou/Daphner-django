FROM python:3.10

WORKDIR /app

RUN git clone https://github.com/amhyou/Daphner-django.git

WORKDIR /app/Daphner-django

RUN pip install -r requirements.txt

RUN python manage.py collectstatic

EXPOSE 8000

CMD daphne -b 0.0.0.0 -p 8000 clicker.asgi:application