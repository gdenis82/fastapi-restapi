FROM python:3.14.0-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv venv /app/.venv && uv sync --frozen --no-dev

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . .
RUN mkdir -p /app/data

# Run the backend entrypoint script
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "-c", "./gunicorn.conf.py", "app.main:app"]
#CMD ["/bin/sh", "-c", "/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000"]
