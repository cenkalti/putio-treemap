FROM python:3.8

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py treemap.py ./
CMD ["/usr/local/bin/gunicorn", "-k", "gevent", "app:app"]
