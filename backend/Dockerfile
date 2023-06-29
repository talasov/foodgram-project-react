FROM python:3.7-slim

WORKDIR /app

RUN pip install django-cors-headers==3.13.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY foodgram/ .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi:application"]