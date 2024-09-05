FROM python:3.12-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

RUN poetry --version

RUN mkdir -p /site_Antona
WORKDIR /site_Antona

COPY . /site_Antona

ARG MY_ENV=production
RUN if [ "$MY_ENV" = "production" ]; then poetry install --no-dev; else poetry install; fi

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]