# Django Bank Application Backend 🏦

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-3.x%7C4.x-green?logo=django)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.x-red)
![JWT](https://img.shields.io/badge/JWT-Authentication-blue)
![GitHub](https://img.shields.io/github/license/Dhareeppa/BACKEND)

A modern, robust backend for a banking application built with **Django** and **Django REST Framework**. This project powers user registration, account management, secure money transfers, and transaction history tracking, secured with **JWT authentication**. 🚀

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Key Files](#key-files)
- [Database Configuration](#database-configuration)
- [Resolving Git Issues](#resolving-git-issues)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview
This repository hosts the backend for a feature-rich banking application. It enables users to register, manage their accounts, perform secure money transfers, and view transaction histories. Built with Django and Django REST Framework, it leverages JWT for secure authentication and provides a clean, scalable API. 🌐

The backend is designed for reliability and ease of use, with serializers for robust data validation and a service layer for handling complex operations like money transfers.

## Features
- 🧑‍💼 **User Registration**: Sign up with username, password, and phone number.
- 💳 **Account Management**: Manage user details including name, date of birth, address, PAN card, Aadhar card, and profile image.
- 💸 **Money Transfers**: Securely transfer funds between accounts with balance validation and transaction logging.
- 📜 **Transaction History**: View detailed records of sent and received transactions.
- 🔍 **Account Lookup**: Find accounts by account number.
- 💰 **Balance Inquiry**: Check current balance and account holder details.
- 🔒 **JWT Authentication**: Secure API endpoints with JSON Web Tokens.

## Tech Stack
- **Framework**: Django, Django REST Framework
- **Authentication**: Django REST Framework Simple JWT
- **Database**: Supports SQLite, PostgreSQL, MySQL, or other Django-compatible databases
- **Utilities**: Python `Decimal` for precise financial calculations
- **Version Control**: Git

## Getting Started

### Prerequisites
- 🐍 Python 3.8 or higher
- 🌐 Django 3.x or 4.x
- 🔗 Django REST Framework
- 🔐 Django REST Framework Simple JWT
- 📦 Git
- 🗄️ Database (SQLite for development, PostgreSQL/MySQL recommended for production)

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Dhareeppa/BACKEND.git
   cd BACKEND
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Create or use a `requirements.txt` file. Install core dependencies:
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the project root:
   ```bash
   SECRET_KEY=your-django-secret-key
   DATABASE_URL=your-database-connection-string  # e.g., sqlite:///db.sqlite3
   DEBUG=True  # Set to False in production
   ```

5. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Run the Server**:
   ```bash
   python manage.py runserver
   ```
   Access the API at `http://localhost:8000/api/`.

## API Endpoints
| Endpoint                     | Method | Description                              | Authentication |
|------------------------------|--------|------------------------------------------|----------------|
| `/api/`                      | GET    | List available API routes                | None           |
| `/api/register/`             | POST   | Register a new user                     | None           |
| `/api/CreateAccount/`        | POST   | Create user account details             | None           |
| `/api/token/`                | POST   | Obtain JWT token pair                   | None           |
| `/api/token/refresh/`        | POST   | Refresh JWT token                       | None           |
| `/api/GetData/`              | GET    | Retrieve all user data                  | Authenticated  |
| `/api/user/me/`              | GET    | Get logged-in user data                 | Authenticated  |
| `/api/transactionsCreate/`   | POST   | Create a transaction                    | None           |
| `/api/get_transaction/`      | GET    | Get user transactions                   | Authenticated  |
| `/api/Receive_transaction/`  | GET    | Get received transactions               | Authenticated  |
| `/api/send/`                 | POST   | Transfer money between accounts         | Authenticated  |
| `/api/current_balance/`      | GET    | Get current account balance             | Authenticated  |
| `/api/find_accountNumber/`   | GET    | Find account by account number          | Authenticated  |
| `/api/transaction_history/`  | GET    | Get enhanced transaction history        | Authenticated  |
| `/api/get_transfer_details/` | GET    | Get details of a specific transfer      | Authenticated  |
| `/api/get_updated_user_data/`| GET    | Get updated user data                   | Authenticated  |

## Key Files
- 📄 **serializers.py**: Defines data validation for users, accounts, transactions, and transfers.
- 🔗 **urls.py**: Maps API endpoints to view functions.
- 🛠️ **views.py**: Handles API requests and responses.
- 💸 **transaction.py**: Implements `MoneyTransferService` for transfer and lookup logic.

## Database Configuration
The project supports any Django-compatible database. For development, use SQLite:
```bash
DATABASE_URL=sqlite:///db.sqlite3
```
For production, PostgreSQL or MySQL is recommended:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```
Update the `.env` file and run migrations:
```bash
python manage.py migrate
```

## Resolving Git Issues
If you encounter `fatal: refusing to merge unrelated histories`:
1. Pull with unrelated histories allowed:
   ```bash
   git pull origin main --allow-unrelated-histories
   ```
2. Resolve conflicts (if any), then commit:
   ```bash
   git add .
   git commit
   ```
3. Push changes:
   ```bash
   git push -u origin main
   ```

## Testing
1. Start the server:
   ```bash
   python manage.py runserver
   ```
2. Use tools like **Postman** or **curl** to test endpoints.
3. Authenticate with `/api/token/` to obtain a JWT for protected endpoints.

## Contributing
Contributions are welcome! 🙌
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request on GitHub.

## License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

🌟 **Built with 💻 and ☕ by [Dhareeppa](https://github.com/Dhareeppa)**