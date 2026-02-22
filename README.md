# Crime Reporting Web Application

## About

This is a Flask-based crime reporting web application that allows citizens to submit complaints, staff to manage and investigate reports, and administrators to oversee the system. The project includes controllers, services, repositories, templates, static assets, and optional ML helpers for image/report verification and summarisation.

## Features

- Public complaint submission with evidence uploads (images, ID proof).
- Staff dashboard for complaint handling and status updates.
- Admin dashboard for user/complaint management.
- Email & OTP utilities for verification and password recovery.
- Optional ML-based helpers for image verification and report summarisation.
- Simple modular architecture separating controllers, services, and repositories.

## Repository structure

- `app/` — application package (controllers, services, repositories, templates, static)
- `app/ml_model/` — ML helper scripts (image verification, summarisation)
- `app/datasets/` — sample datasets (CSV)
- `app/crime_image/` — storage structure for evidence images and ID proofs
- `util/` — utilities (`db_connection.py`, `mail_handler.py`, `encryption.py`, `otp_generate.py`)
- `admin_user_table_schema.sql`, `staff_table_schema.sql` — SQL schema files
- `app.py`, `app_admin.py`, `app_public.py`, `staff_app.py` — entrypoint scripts
- `requirements.txt` — Python dependencies

## Requirements

- Python 3.9+
- pip
- SQLite/MySQL/Postgres (or other DB as configured)

## Installation (local development)

1. Clone the repo:

```bash
git clone https://github.com/<your-username>/<repo>.git
cd <repo>
```

2. Create and activate a virtual environment:

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Unix/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (do not commit it). Example values:

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=replace-with-a-secret
DATABASE_URL=sqlite:///crime.db
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=you@example.com
MAIL_PASSWORD=yourpassword
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Notes:
- Keep credentials and private keys out of version control. Use environment variables or a secrets manager.
- If you use a different DB (MySQL/Postgres), update `DATABASE_URL` accordingly and run the SQL schema files in your DB.

## OpenRouter API key (setup)

This project optionally uses OpenRouter for language-model features (summarisation, verification helper). To use it:

1. Visit https://openrouter.ai/ and sign up for an account.
2. Create a new API key from the dashboard (usually under API keys).
3. Copy the API key and add it to your `.env` as `OPENROUTER_API_KEY`.

Quick test (curl):

```bash
curl https://api.openrouter.ai/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

Where the code in `app/ml_model/openrouter.py` will read the key from the environment. If you need to change the code location, set the same env var in your deployment environment.

## Database initialization

Use the provided SQL schema files to create required tables. Example using SQLite (adjust for your DB):

```bash
sqlite3 crime.db < admin_user_table_schema.sql
sqlite3 crime.db < staff_table_schema.sql
```

For MySQL/Postgres, run the SQL files with your preferred client or migration tool.

## Running the application

Development run (single default app):

```bash
python app.py
```

Other entrypoints:

```bash
python app_public.py   # public-facing site
python app_admin.py    # admin site
python staff_app.py    # staff site
```

By default the app will bind to `127.0.0.1:5000` unless configured otherwise via env vars.

## ML helpers

The `app/ml_model/` directory contains helper scripts for image verification and summarisation. These are optional and may require additional dependencies or API keys. Large model weights or datasets should not be committed — use cloud storage or release assets instead.

## Static files & uploads

- Evidence and ID images are placed under `app/crime_image/`; ensure upload directories have appropriate permissions.
- Do not commit user uploads or private certificates — add them to `.gitignore`.

## Tests

There is a minimal `test.py` for quick sanity checks. Expand with pytest or unittest for a fuller test suite.

## Deployment

For production use consider a WSGI server such as Gunicorn and a process manager. Example (Linux):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Set environment variables (including `OPENROUTER_API_KEY`, DB credentials, and mail credentials) in your host environment or use a secrets manager.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make changes and run tests
4. Commit with a descriptive message (see examples below)
5. Open a pull request

Recommended commit message examples:

- `chore: initial import — add project skeleton`
- `feat: add public complaint submission endpoint`
- `fix: sanitize user-uploaded filenames`
- `docs: improve README and setup instructions`

## Security & privacy

- Remove or redact any real user data before sharing or publishing
- Rotate API keys and passwords if they have been exposed
- Use HTTPS in production and secure file upload handling

## License

This project is licensed under the MIT License. See the `LICENSE` file or below for details.

---

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
