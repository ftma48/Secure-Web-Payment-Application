# Secure Web Payment Application

A Django web application developed as a university project. It supports user registration, authentication, payments between users, payment requests, and account administration.

## Features

* User registration and login
* Payments between registered users
* Payment requests
* Account management
* Administrative functionality
* Currency conversion through a REST API
* Role-based access controls

## Technologies

* Python
* Django
* SQLite
* REST APIs
* HTML and CSS

## Security

The application includes authentication, access controls, and security measures explored during development.

This is an educational project, not a production payment system. Do not use it to process real payments or store real financial information.

## Running Locally

Requires Python 3.14.

1. Clone the repository and open the project folder.
2. Create and activate a virtual environment:

   python -m venv .venv
   .venv\Scripts\activate

3. Install dependencies:

   python -m pip install -r requirements.txt

4. Generate a Django secret key and set the
   DJANGO_SECRET_KEY environment variable.

5. Create the local database:

   python manage.py migrate

6. Start the development server:

   python manage.py runserver

## Project Structure

* `payapp/` — payment-related functionality
* `register/` — registration and authentication
* `restservice/` — currency conversion REST service
* `templates/` — HTML templates
* `webapps2026/` — Django project configuration

## Notes

Local databases, private keys, and development environment files are excluded from the repository.
