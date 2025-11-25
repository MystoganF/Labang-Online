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

Open `http://127.0.0.1:8000/accounts/register/` to register and verify.

**Setup Gmail Recovery**

```
notepad .env
```

Paste this in the .env

```
EMAIL_HOST_USER=lenonleenatividad4@gmail.com
EMAIL_HOST_PASSWORD=xsvv kuet jktf wrtd
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

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

5. Admin Dashboard Instructions

The Admin Dashboard allows authorized staff to manage users, certificate requests, and incident reports.

Access Requirements

User must have is_staff=True or is_superuser=True.
Only staff users can access admin URLs.
Creating an Admin User
Create a superuser (if none exists):
py manage.py createsuperuser

Or promote an existing user to staff:

py manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(username='your_username')
>>> user.is_staff = True
>>> user.save()

URLs
Feature	URL
Admin Dashboard	/accounts/admin/dashboard/
User Management	/accounts/admin/users/
Certificate Management	/accounts/admin/certificates/
Report Management	/accounts/admin/reports/

All admin views require login. Unauthorized users are redirected to /accounts/personal_info/.

Key Features

- Dashboard Statistics: Users, certificates, and reports overvie
- User Management: Verify, activate/deactivate users, view details
- Certificate Management: Approve/reject payments, update claim status
- Report Management: Update status, delete reports
- Activity Tracking: Automatic logging via Django
- Create announcements
- Security
- Authentication required
- CSRF protection on all forms
- SQL injection prevention through Django ORM
- Only staff can perform admin actions


## Team members
- Lenon Lee O. Natividad 
- Lead Developer
- lenonlee.natividad@cit.edu

- Bryne Kendrick P. Nuñez
- Frontend Developer
- brynekendrick.nunez@cit.edu

- Moniquo Nicole C. Mosende
- Backend Developer
- moniquonicole.mosende@cit.edu

