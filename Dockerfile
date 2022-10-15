FROM python:3.8

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py treemap.py ./
EXPOSE 8080
CMD ["/usr/local/bin/gunicorn", "--bind=0.0.0.0:8080", "-k", "gevent", "app:app"]
