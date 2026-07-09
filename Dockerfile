# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir build

COPY requirements/base.txt /tmp/requirements/base.txt
RUN pip install --no-cache-dir -r /tmp/requirements/base.txt

COPY . .

RUN pip install --no-cache-dir --no-deps . \
    && python -m build --wheel


FROM python:3.12-slim AS development

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=base /usr/local /usr/local
COPY requirements/ /tmp/requirements/

RUN pip install --no-cache-dir -r /tmp/requirements/dev.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.12-slim AS production

WORKDIR /app

COPY --from=base /usr/local /usr/local
COPY --from=base /app/dist /tmp/dist

RUN pip install --no-cache-dir /tmp/dist/*.whl && rm -rf /tmp/dist

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
