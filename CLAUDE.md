# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single-page Flask app that pings an address (hostname or IP) from the server and shows the round-trip time. Live demo: https://ping.greg.ca. There is no test suite and no database.

## Commands

Production (the committed configuration):

```bash
docker-compose up -d --build   # gunicorn on container port 5000, published on host port 8102
```

Lint (the same check the production Docker build runs; a flake8 failure fails the build):

```bash
cd services/web && flake8 --ignore=E501,W503,F401 .
```

## Dev/prod switching

The repo holds the PROD configuration. Dev uses locally excluded files (listed in `.git/info/exclude`): `docker-compose.DEV.yml` and `services/web/Dockerfile.DEV`. `./to-dev.sh` and `./to-prod.sh` swap them in and out by renaming:

- `./to-dev.sh` renames the tracked `docker-compose.yml` and `services/web/Dockerfile` to `*.PROD*`, and moves the DEV versions into their place. Dev runs Flask's debug server on port 5000 with `services/web/` bind-mounted to `/app`, so code changes reload live.
- `./to-prod.sh` reverses it.

While in DEV mode the tracked `docker-compose.yml` and `Dockerfile` show as modified and the `*.PROD*` files show as untracked. **Run `./to-prod.sh` before committing**, so the dev versions aren't committed. If `docker-compose.PROD.yml` exists, the working tree is in DEV mode.

`test.py` (also excluded) is a scratch script for redirect-following with `requests`; it isn't part of the app or a test suite.

## Architecture

All the app code is in `services/web/project/__init__.py`; `manage.py` only wraps it in a `FlaskGroup` so gunicorn can load `manage:app`.

- `GET /` shows the form with the visitor's IP prefilled (from the first `X-Forwarded-For` entry if present, since it runs behind a reverse proxy) but doesn't ping it: an unresponsive IP takes the full timeout, and the first page load would hang. `POST /` (the form) redirects to `/<submitted address>`, so every result has a shareable URL. The address is encoded with `quote(..., safe="")` in that redirect; without it, an address starting with `/` made a `//host` redirect to another site.
- `GET /<address>` calls `check_ping()`, which uses `ping3.ping()` (5 s timeout) plus `socket.gethostbyname()` to show the resolved IP when it differs from the input, then renders `templates/home.html`.
- Pinging is IPv4-only: ping3 4.0.8 and `socket.gethostbyname()` only handle IPv4, and the production container's Docker network has IPv6 disabled. `check_ping()` answers IPv6 literals with an "aren't supported" message before trying.
- `check_ping()` builds its result messages with `Markup(...).format(...)`, so the markup in the format string is kept and `address`/`result_ip` are HTML-escaped. Keep using that (not f-strings) for any message that includes user input; the template renders `page_body` without `|safe`.
- The static folder is `project/assets/` (not `static/`), served via `url_for('static', ...)`. jQuery is vendored there and only shows the loading spinner on submit.
- Styling is Tailwind 4 + daisyUI 5 from jsDelivr CDNs (`bumblebee` theme); there is no frontend build step.
- `templates/custom.headers` is an optional, gitignored include (`ignore missing`) for per-deployment `<head>` content such as analytics.
- Python is 3.9 (`python:3.9.21-slim`); direct dependencies are pinned in `services/web/requirements.txt` (transitive ones such as Jinja2 and MarkupSafe aren't, so they can change between builds), and pip is pinned in the Dockerfile. The production image is multi-stage: the builder stage lints and builds wheels, and the final stage runs as the non-root `app` user.
