## Labang Online

The primary purpose of Labang Online is to digitize barangay-level services in Barangay Labangon, Cebu City. This project targets long queues and paper-based processes by enabling online access to services like certificate requests, complaints, and inquiries.

## Tech stack used

- Django
- Supabase
- HTML/CSS/JavaScript

## Setup & run instructions

1) Ensure Python 3.13+ is installed. Verify: `py -V`
2) Option A: Virtual environment (recommended)

```
py -m venv .venv
# If activation scripts are missing, you can skip activation and use `py -m pip --user` below.
```

3) Install dependencies

```
py -m pip install --user django django-environ phonenumbers
pip install dj-database-url
pip install python-dotenv
pip install psycopg2-binary
pip install psycopg
pip install whitenoise
pip install google-generativeai
```

4) Initialize database and run server

```
py manage.py migrate
py manage.py runserver
```

Open `http://127.0.0.1:8000/` to register and verify.

**Setup Gmail Recovery**

```
python setup_gmail_recovery.py
py manage.py runserver
```

**Supabase (Session Pooler) setup**

1) Install packages:
```
py -m pip install --user psycopg2-binary dj-database-url python-dotenv
```

2) In the Supabase dashboard → Project → Connect → Connection Info, copy the Session Pooler URL. It looks like:
```
postgresql://postgres:YOUR_PASSWORD@aws-0-<project-ref>.pooler.supabase.com:5432/postgres
```
Append `?sslmode=require`.

3) Create a `.env` in the project root:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@aws-0-<project-ref>.pooler.supabase.com:5432/postgres?sslmode=require
```

4) Migrate and run to verify the connection:
```
py manage.py migrate
py manage.py runserver
```

5. Admin Dashboard (Django)

Use Django’s built‑in admin for staff operations.

Access

Local: `http://127.0.0.1:8000/admin/`
After deploy: `https://csit327-g7-labang-online.onrender.com//admin/`

Requirements

- Your account must have `is_staff=True` (recommended: also `is_superuser=True`).
- Anonymous users are redirected to the admin login.
- Logged‑in non‑staff users see 403 Forbidden.

Create an Admin Account

Create a superuser:

```
py manage.py createsuperuser
```

Promote an existing user:

```
py manage.py shell
from accounts.models import User
u = User.objects.get(username='your_username')
u.is_staff = True
u.is_superuser = True  # optional but recommended
u.save()
```

Troubleshooting

- 403 Forbidden at `/admin/`: ensure your user has `is_staff=True`.
- Redirect to login: log in with a staff/superuser account.
- Static files missing in production: run `py manage.py collectstatic` and ensure `whitenoise` is installed.

Deploy Render

- https://labang-online.onrender.com/


## Team members

Project Managers:
Product Owner: Andre Salonga
Scrum Master: Kean Maverick Saligue
Business Analyst: Andrey Reyes

Developers:
- Lenon Lee O. Natividad 
- Lead Developer
- lenonlee.natividad@cit.edu

- Bryne Kendrick P. Nuñez
- Frontend Developer
- brynekendrick.nunez@cit.edu

- Kean Maverick W. Saligue
- Full-Stack Developer
- keanmaverick.saligue@cit.edu

