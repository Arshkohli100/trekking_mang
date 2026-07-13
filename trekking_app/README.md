# Trekking Management Application

## How to Run (Windows, VS Code)

1. Open this folder in VS Code
2. Open Terminal (Ctrl + `)
3. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the app:
   ```
   python app.py
   ```
6. Open browser at http://127.0.0.1:5000

## Admin Login (pre-created)
- Email: admin@trek.com
- Password: admin123

## Roles
- Admin: manage treks, staff, users, bookings
- Staff: register (needs admin approval), manage assigned treks
- User: register, book treks, view history

## Tech Stack
- Flask (backend)
- Jinja2 + HTML + Bootstrap (frontend)
- SQLite (database)
