FROM python:3.8-alpine3.11

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
CMD ["flask", "run"]
