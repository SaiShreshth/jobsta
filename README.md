# MSRIT Job Portal

A production-grade web application for job postings at MSRIT, built with Flask, PostgreSQL, and Tailwind CSS.

## Features

- Passwordless magic-link email authentication
- Job posting and application tracking
- Admin dashboard
- Mobile-first responsive design

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables: copy `.env.example` to `.env` and fill in
6. Run migrations: `flask db upgrade`
7. Run the app: `flask run`

## Deployment

Deployed on Render with PostgreSQL Neon.