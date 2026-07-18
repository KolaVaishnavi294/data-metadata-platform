FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask flask_sqlalchemy psycopg2-binary marshmallow

EXPOSE 5000

CMD ["python", "app.py"]