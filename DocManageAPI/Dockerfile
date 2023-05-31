FROM python:3.11.3-alpine3.18
WORKDIR /app

RUN apk add gcc musl-dev
RUN addgroup -S django && adduser -S django -G django

COPY --chown=django:django requirements.txt .

USER django
RUN pip install --no-cache-dir --user -r requirements.txt

USER root
COPY --chmod=755 . .
RUN mkdir -p /app/storage && chown -R django:django /app/storage

USER django

EXPOSE 8000

# Start the application
CMD ["./run.sh"]