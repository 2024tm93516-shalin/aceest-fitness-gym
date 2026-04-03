FROM python:3.11-slim

LABEL maintainer="aceest-gym"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY tests/ ./tests/

RUN adduser --disabled-password --gecos "" gymuser \
    && chown -R gymuser /app

USER gymuser

EXPOSE 5000

CMD ["python", "app.py"]
