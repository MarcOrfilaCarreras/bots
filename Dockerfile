FROM python:alpine3.19

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./bots /app/bots
COPY ./run.py /app/run.py

CMD ["python", "run.py"]
