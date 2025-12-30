# MSRIT Job Portal

A production-grade web application for job postings at MSRIT, built with Flask, PostgreSQL, and Tailwind CSS.

## Features

- Passwordless magic-link email authentication (only @msrit.edu emails)
- Job posting and application tracking
- Admin dashboard with analytics
- User dashboard with applications and notifications
- Reviews and ratings for jobs
- Mobile-first responsive design
- Secure cookies and CSRF protection

## Tech Stack

- Backend: Flask (Python)
- Database: PostgreSQL (Neon)
- Frontend: Jinja2 templates + Tailwind CSS
- Email: Flask-Mail
- Deployment: Render

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables: copy `.env.example` to `.env` and fill in
6. Run migrations: `flask db upgrade`
7. Build CSS: `npx tailwindcss -i src/input.css -o static/css/main.css`
8. Run the app: `flask run`

## Environment Variables

- DATABASE_URL: PostgreSQL connection string
- SECRET_KEY: Flask secret key
- EMAIL_SERVER: SMTP server
- EMAIL_PORT: SMTP port
- EMAIL_USERNAME: Email username
- EMAIL_PASSWORD: Email password

## Deployment

Deployed on Render with PostgreSQL Neon.

Use `render.yaml` for configuration.