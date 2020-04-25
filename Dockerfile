FROM python:3.8-alpine3.11

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py treemap.py ./
CMD ["/bin/bash", "-c", "exec gunicorn --bind=0.0.0.0:$PORT -k gevent -w 1 app:app"]
