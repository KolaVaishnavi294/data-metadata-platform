FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    pandas \
    requests \
    openlineage-python

CMD ["python", "run_pipeline.py"]