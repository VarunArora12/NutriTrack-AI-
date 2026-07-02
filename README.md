# 🥗 NutriTrack AI

NutriTrack AI is a clean full-stack nutrition tracking app built with React, Vite, Tailwind CSS, Flask, and SQLite.

It includes database-backed authentication, user profiles, meal logging, Indian food search, nutrition estimation, daily tracking, and weekly analytics charts.

## Tech Stack

- React + Vite
- Tailwind CSS

### Backend
- Flask
- SQLite
- Werkzeug password hashing
- Secure database-backed session tokens
- Recharts

## Project Structure

```txt
nutritrack-ai/
├── frontend/
│   ├── src/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles/index.css
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
└── backend/
    ├── app.py
    ├── auth.py
    ├── database.py
    ├── nutrition.py
    ├── requirements.txt
    └── vercel.json
```

## Run Locally

### Backend

cd backend

pip install -r requirements.txt

python app.py

### Frontend

cd frontend

npm install
npm run dev -- --host 0.0.0.0 --port 5001
```

The app runs on `http://localhost:5001`.

## API Overview

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/profile`
- `PUT /api/profile`
- `GET /api/foods?q=roti`
- `POST /api/nutrition/estimate`
- `GET /api/meals?date=YYYY-MM-DD`
- `POST /api/meals`
- `DELETE /api/meals/:id`
- `GET /api/dashboard/today`
- `GET /api/analytics/week`

## Notes

- The built-in food database lives in `backend/nutrition.py`.
- Session tokens are generated securely, hashed before storage, and expire after 7 days.
- The SQLite database is created automatically in `backend/instance/nutritrack.db`.
