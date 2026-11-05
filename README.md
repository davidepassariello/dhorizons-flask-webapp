# DHorizons - Digital Humanities Student Portal

**Flask · Python · SQLite · SQLAlchemy · HTML · CSS · JavaScript**

DHorizons is an academic prototype of a student-run portal for a Digital Humanities Master's programme in Naples. It was developed for a **Web Technologies** course. This repository is a privacy-conscious **portfolio edition**, not an official university website or a production-ready service.

## Features

- Public home page with a content carousel
- News posts, dated events and embedded YouTube lessons
- Search across posts, events and lessons
- Protected admin dashboard for adding and deleting content
- Local SQLite database with SQLAlchemy models
- Optional image attachments to posts and events
- Responsive presentation using Jinja templates, CSS and JavaScript

## Local setup

Requires Python 3.10+.

```bash
python -m venv .venv
```

Activate the virtual environment (`.venv\Scripts\activate` on Windows PowerShell, or `source .venv/bin/activate` on macOS/Linux), then:

```bash
pip install -r requirements.txt
python create_db.py
python app.py
```

Open `http://127.0.0.1:5000` in a browser. The database is created empty. You can browse the site without signing in; adding content requires setting administrator credentials as described below.

### Optional demo administrator login

Generate a password hash locally (do not publish the password or hash):

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('CHOOSE_A_STRONG_PASSWORD'))"
```

Set `DHORIZONS_ADMIN_PASSWORD_HASH` to the output and optionally `DHORIZONS_ADMIN_USERNAME` (default `admin`). Also set `FLASK_SECRET_KEY` to a strong random value. In **Windows PowerShell**, use `$env:VARIABLE_NAME = 'value'`; in macOS/Linux use `export VARIABLE_NAME='value'`. Set these in the same terminal session before running `python app.py`.

Example for generating a session secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

The app deliberately has **no default administrator password**.

## Project architecture

- `app.py` — Flask routes, models, session-based demo login and admin operations
- `templates/` — Jinja pages (home, news, events, lessons, search, admin)
- `static/styles.css`, `static/readmore.js` — styling and page interactions
- `static/img*_home.svg` — generic replacement illustrations, without student photographs
- `create_db.py` — initializes a fresh, empty local SQLite database

## Privacy and publication notes

Original student photographs, personal contact details, uploads and the original SQLite database were intentionally **not** included. The background graphics are generic substitutes. The original project was created collaboratively; this repository is a cleaned demonstration of the Flask application, not a claim of sole authorship of all design and editorial material.

## Security and limitations

This is a local educational prototype, **not production software**. The portfolio edition removes the hard-coded secret and password, requires authentication on administrative actions, adds CSRF checks and limits uploads to image extensions and 5 MB. Upload validation is basic and should be strengthened (including content inspection), and production deployment would require more hardening, testing and proper session/configuration management.

## Screenshots

Add screenshots of the local demo to an `images/` folder if you want to showcase the interface on the repository page.
