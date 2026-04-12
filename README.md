# sifr-notes

A minimal self-hosted notes app with markdown support, built on a FastAPI backend and HTMX frontend with no JavaScript.

## Stack

- **Backend:** FastAPI, SQLAlchemy (async), Alembic, PostgreSQL
- **Frontend:** HTMX, Jinja2, plain CSS
- **Auth:** Single-user, cookie-based session (itsdangerous)
- **Infrastructure:** Docker + docker-compose


## Running Locally

**Prerequisites:** Docker, Docker Compose

```zsh
git clone https://github.com/werkd/sifr-notes.git
cd sifr-notes && cp .env.example .env
docker-compose up --build
```

App runs at `https://localhost:8000`.

## Project Status 
Currently under (active) development.
