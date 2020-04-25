FROM python:3.8

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py treemap.py ./
CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind=0.0.0.0:$PORT -k gevent -w 1 app:app"]
