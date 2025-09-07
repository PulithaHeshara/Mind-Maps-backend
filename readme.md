# 🖥️ Mind Map Whiteboard - Backend

A collaborative **mind mapping web app** backend built with **Django + Django REST Framework**.

---

## 🌟 Features

- REST API for nodes, edges, and boards
- WebSocket support for real-time collaboration
- JWT authentication and permissions
- Room management for multiple collaborative sessions

---

## 📦 API Endpoints

### 🔑 Authentication
- `POST /board/login` – Log in with username & password → returns JWT tokens  
- `POST /board/token/refresh/` – Refresh access token  

### 🗂️ Boards
- `POST /board/create` – Create a new board  

### 🔌 WebSockets
- `ws://<your-domain>/ws/board/<room_name>/`  
  - Join a collaborative board session

---

## 🛠️ Setup / Installation

1. **Clone the repo**

```bash
git clone https://github.com/yourusername/Mind-Maps-backend.git
cd Mind-Maps-backend
```
2. **Create & activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt

```
4. **Set up environment variables**
```bash
Create a .env file in the project root:

DJANGO_SECRET_KEY=<YOUR_SECRET_KEY>
DEBUG=True
DATABASE_URL=<YOUR_DATABASE_URL>

```
5. **Apply migrations**
```bash
python manage.py migrate
```

6. **Run the backend**
```bash
python manage.py runserver
```