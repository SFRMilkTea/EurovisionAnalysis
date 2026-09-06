# Eurovision Analysis

## Frontend (React)

The React client lives in `client`; FastAPI remains in `app` and provides both the API and
the production static-file host. The UI uses the existing session cookie, so no token is stored
in the browser.

For local frontend work, start FastAPI on port 8000 and then run these commands in a second
terminal:

```bash
cd client
pnpm install
pnpm dev
```

Vite runs at `http://localhost:5173` and proxies API requests to FastAPI. For a production
build, run `pnpm build`; it writes the bundle to `app/static`. Docker builds that bundle
automatically in its Node build stage.

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
