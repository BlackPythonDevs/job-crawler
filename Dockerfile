FROM python:3.14-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir . \
    && mkdir -p /var/log/job-crawler

EXPOSE 8080

CMD ["job-crawler"]
