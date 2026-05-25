# 🔐 AIEngineer Authentication System

A Django REST Framework-based authentication system implementing:
- OTP-based email verification
- Cookie-based authentication
- Protected user endpoints
- Swagger API documentation

---

## ⚙️ Tech Stack
- Django
- Django REST Framework
- drf-yasg (Swagger)
- SQLite (default DB)

---

## 🚀 Setup Instructions

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 3. Run server
python manage.py runserver