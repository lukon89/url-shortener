# URL Shortener

A simple URL shortener REST API built with Django and Django REST Framework. Accepts a long URL, returns a short code, and resolves short codes back to the original URL.

> **Note:** This is a simple learning project. It intentionally omits:
> - **Dockerfile** — run locally with a plain virtualenv
> - **Makefile** — all commands are documented below
> - **HTTP redirects** — `GET /api/shrt/{code}/` returns the original URL as JSON, not a `301`/`302` redirect. The caller decides what to do with it.

## Requirements

- Python 3.12+
- pip

## Setup

```bash
git clone <repo>
cd url-shortener

python -m venv .venv
source .venv/bin/activate

pip install -r requirements-dev.txt
```

## Running the server

```bash
python manage.py runserver
```

Server starts at `http://localhost:8000`.

## API

### Shorten a URL

```
POST /api/shrt/
Content-Type: application/json

{"url": "https://example.com/very/long/url"}
```

Response `200 OK`:
```json
{"short_url": "http://localhost:8000/shrt/aB3xZ9"}
```

Errors:

| Status | Reason |
|---|---|
| `400` | Missing or invalid `url` field |
| `500` | Internal error |

---

### Resolve a short URL

```
GET /api/shrt/{code}/
```

Response `200 OK`:
```json
{"long_url": "https://example.com/very/long/url"}
```

Errors:

| Status | Reason |
|---|---|
| `404` | Code not found |
| `500` | Corrupted data in storage |

## Manual testing

**1. Create a shortened URL:**
```bash
curl -X POST http://localhost:8000/api/shrt/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

**2. Retrieve the long URL from a code:**
```bash
curl http://localhost:8000/api/shrt/<code>/
```

## Testing

### Unit tests

```bash
python manage.py test api.tests.test_views
```

### E2E tests

Uses `LiveServerTestCase` — starts a real HTTP server automatically, no manual setup needed.

```bash
python manage.py test api.tests.test_e2e
```

### All tests

```bash
python manage.py test api
```

## Dependencies

| File | Used for |
|---|---|
| `requirements.txt` | Production |
| `requirements-dev.txt` | Local development and testing |

---

*Note for transparency: This README was written with the assistance of AI (Claude). But whole project structure and logic was written by me.*
