# Data Security Authentication Demo

## Overview
- Web app for local user authentication (`http://localhost:5000`).
- Uses Flask + SQLite (SQL database mandatory).
- User credentials are stored with SHA-256 hashed passwords (no plaintext storage).
- Admin and user role differentiation with separate access control.

## Requirements Implemented
- Login page with separate `username` and `password` fields.
- Admin (first DB record) and standard user role checks.
- Password hashing with SHA-256 in `hash_password`.
- "Forgot the password?" flows to reset without restoring the old password.
- Database initialization script invites first-user admin entry.

## Local setup
1. Install dependencies:
   - `pip install flask`
2. Run app:
   - `python app.py` (first run auto-creates `users.db`)
3. Open `http://127.0.0.1:5000`.

## Preseeded accounts
- Admin: username `admin`, password `admin123`
- User: username `user`, password `user123`

## Security notes
- Passwords are hashed through `hashlib.sha256` and stored in `users.db`.
- The system cannot retrieve forgotten passwords (one-way hash). Reset generates new hash for new password.

## Files
- `app.py` (main Flask app, DB & auth logic)
- `templates/login.html`, `forgot.html`, `reset.html`, `admin.html`, `user.html`
- `users.db` (created at runtime)
