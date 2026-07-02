# 🥗 NutriTrack AI

A modern full-stack AI-powered nutrition tracking application that helps users log meals, estimate nutrition, monitor daily calorie intake, and visualize weekly nutrition trends.

🔗 **Live Demo:** https://nutri-track-ai-j.vercel.app  
💻 **GitHub Repository:** https://github.com/VarunArora12/NutriTrack-AI

---

## ✨ Features

- 🔐 Secure authentication (Sign Up / Login / Logout)
- 👤 User profile management
- 🍽️ Meal logging with nutrition tracking
- 🔎 Indian food search
- 🤖 AI-powered nutrition estimation from meal descriptions
- 📊 Daily calorie, protein, carbs & fat dashboard
- 📈 Weekly nutrition analytics
- 🔒 Secure session management
- ☁️ Deployed on Vercel

---

## 🛠️ Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router
- Recharts

### Backend
- Flask
- Supabase (Database)
- Werkzeug (Password Hashing)
- Flask-CORS

### Deployment
- Vercel (Frontend)
- Vercel Serverless Functions (Backend)

---

## 📸 Screenshots

> Add screenshots inside a `screenshots/` folder.

| Login | Dashboard |
|-------|-----------|
| ![](screenshots/login.png) | ![](screenshots/dashboard.png) |

| Meal Log | Analytics |
|----------|-----------|
| ![](screenshots/meal-log.png) | ![](screenshots/analysis.png) |

---

## 🚀 Live Demo

Visit the application here:

**https://nutri-track-ai-j.vercel.app**

---

## 📁 Project Structure

```text
nutritrack-ai/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── database.py
│   ├── nutrition.py
│   ├── requirements.txt
│   └── vercel.json
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/VarunArora12/NutriTrack-AI.git

cd NutriTrack-AI
```

---

### 2. Backend Setup

```bash
cd backend

pip install -r requirements.txt

python app.py
```

---

### 3. Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

Backend runs at:

```
http://localhost:5002
```

---

## 🔑 Environment Variables

### Backend

Create a `.env` file inside the `backend` folder.

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_secret_key
```

### Frontend

Create a `.env` file inside the `frontend` folder.

```env
VITE_API_URL=http://localhost:5002/api
```

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint |
|---------|----------|
| POST | `/api/auth/signup` |
| POST | `/api/auth/login` |
| POST | `/api/auth/logout` |
| GET | `/api/auth/me` |

### Profile

| Method | Endpoint |
|---------|----------|
| GET | `/api/profile` |
| PUT | `/api/profile` |

### Meals

| Method | Endpoint |
|---------|----------|
| GET | `/api/meals` |
| POST | `/api/meals` |
| DELETE | `/api/meals/:id` |

### Dashboard

| Method | Endpoint |
|---------|----------|
| GET | `/api/dashboard/today` |
| GET | `/api/analytics/week` |

### Nutrition

| Method | Endpoint |
|---------|----------|
| GET | `/api/foods?q=` |
| POST | `/api/nutrition/estimate` |

---

## 🔒 Security Features

- Password hashing using Werkzeug
- Secure session tokens
- Database-backed authentication
- Protected API routes
- CORS protection
- Environment variables for sensitive credentials

---

## 🎯 Future Improvements

- 📷 AI food image recognition
- 🎙️ Voice meal logging
- 📱 Progressive Web App (PWA)
- 🌙 Dark mode
- 🍎 Barcode scanner
- 🥗 Personalized meal recommendations
- 🔔 Daily reminders
- 📅 Monthly nutrition reports

---

## 👨‍💻 Author

**Varun Arora**

- GitHub: https://github.com/VarunArora12
- LinkedIn: https://www.linkedin.com/in/varun-arora1

---

## ⭐ Support

If you found this project useful, consider giving it a **⭐ Star** on GitHub!
