FROM python:3.10-slim

RUN apt-get update \
        && apt-get install -y --no-install-recommends \
                ca-certificates \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY /app/ /app/

ENTRYPOINT ["python", "/app/main.py"]
