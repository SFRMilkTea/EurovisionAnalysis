# Eurovision Analysis

## Deploy to Amvera Cloud

Amvera builds the application from `Dockerfile`; `docker-compose.yml` is not used.
The container applies Alembic migrations at startup and listens on port `8000`.

In the Amvera project settings, add these environment variables:

- `DATABASE_URL` — a PostgreSQL SQLAlchemy URL, for example
  `postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE`.
- `SECRET_KEY` — a long random secret value.
- `ALGORITHM` — `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES` — for example `60`.

Do not add `app/.env` to Git: it is intended only for local development.
