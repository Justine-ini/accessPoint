# accessPoint

accessPoint is a Django marketplace application for managing restaurants, menus,
customers, carts, checkout, and orders. It is structured as a multi-app Django
project with separate modules for accounts, vendors, menu management,
marketplace browsing, customers, and orders.

## Features

- Custom email-based user model with vendor and customer roles
- Vendor onboarding, approval status, profiles, and weekly opening hours
- Menu category and food item management for vendors
- Marketplace listing, search, cart, checkout, and order flow
- Customer profiles, order history, and vendor-facing order views
- Payment model support for Paystack and Flutterwave transaction records
- PostGIS-backed profile location storage through Django GIS fields
- Email notification templates for account verification, password reset, and
  vendor approval events

## Tech Stack

- Python 3.13
- Django 5.2
- PostgreSQL with PostGIS
- Django GIS / GDAL
- Pillow for uploaded images
- python-dotenv for environment configuration
- HTML, CSS, JavaScript, and Bootstrap-style templates

## Project Structure

```text
accessPoint_main/   Django project settings, URLs, and static assets
accounts/           Custom user model, profiles, auth views, and emails
vendor/             Vendor profiles, licenses, approval, and opening hours
menu/               Categories and food items
marketplace/        Listings, search, cart, checkout, and tax logic
customers/          Customer dashboard and order history
orders/             Payments, order records, ordered foods, and vendor totals
templates/          Shared and app-specific Django templates
static/             Frontend assets
```

## Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL with the PostGIS extension enabled
- GDAL installed on your machine and available to Django GIS
- A virtual environment tool such as `venv`

Do not commit GDAL wheel files or local virtual environments to the repository.
Install platform-specific GIS dependencies locally instead.

### Local Setup

Clone the repository:

```bash
git clone https://github.com/Justine-ini/accessPoint.git
cd accessPoint
```

Create and activate a virtual environment:

```bash
python -m venv env
env\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file from the sample:

```bash
copy .env-sample .env
```

Fill in the required database and app settings:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=accesspoint
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

Run migrations and start the development server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Notes

- The project uses Django GIS and expects local GDAL/PostGIS setup.
- Payment provider keys, Google API keys, and email credentials should live in
  `.env`, not in source control.
- Uploaded media and collected static output are ignored by git.

## Status

This repository is a portfolio project and active cleanup target. The next
professional improvements should be tests, CI, deployment notes, screenshots,
and clearer environment documentation.
