# Project RIFT - Remote Intrusion Forensics Tool (Backend)

## Overview

**Project RIFT** is a remote intrusion forensics tool designed for cybersecurity coursework and research. This repository contains the complete backend server, which acts as the central hub for receiving, processing, and storing forensic data collected from remote agents deployed on compromised machines. The backend exposes a secure REST API and WebSocket interface for agent communication and provides endpoints for a React.js dashboard (not included here) to visualize and analyze forensic evidence.

---

## Project Overview

- **Project RIFT** is a comprehensive remote forensics platform.
- The system consists of:
  - A **Golang agent** (not included) that collects forensic data from endpoints.
  - This **Django backend server** (provided here) for data ingestion, processing, and storage.
  - A **React.js frontend dashboard** (not included) for visualization and analysis.
- The backend is responsible for:
  - Handling REST API and WebSocket endpoints.
  - Managing the database and data models.
  - Securely processing and storing forensic data.
  - Integrating with the frontend dashboard for data retrieval and visualization.

---

## Backend Features

- **RESTful API** for device registration, authentication, and data ingestion (passwords, browser history, screenshots).
- **JWT-based authentication** with role-based access control (user/agent).
- **WebSocket server** (via Django Channels) for real-time, bidirectional communication with agents.
- **Command and control**: Send commands, request files, and receive live data from agents.
- **Custom user model** for extensibility.
- **Swagger/OpenAPI** documentation for all REST endpoints.
- **CORS support** for secure frontend-backend integration.
- **MySQL database** support (default; can be adapted to PostgreSQL with manual changes in `settings.py`).
- **Admin interface** for manual data inspection and management.
- **Extensible permissions system** for fine-grained API access.
- **Data serialization** for secure and structured API responses.

---

## Backend Architecture & Folder Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── admin.py           # Django admin registrations
│   ├── apps.py            # App configuration
│   ├── consumers.py       # WebSocket consumers (agent communication)
│   ├── models.py          # Database models (CustomUser, Devices, Passwords, etc.)
│   ├── permissions.py     # Custom permission classes (role-based, agent-specific)
│   ├── routing.py         # WebSocket URL routing
│   ├── serializers.py     # DRF serializers for all models
│   ├── tests.py           # Unit tests (template)
│   ├── urls.py            # REST API endpoint routing
│   └── views.py           # API views (CRUD, authentication, registration)
├── RIFT/
│   ├── __init__.py
│   ├── asgi.py            # ASGI application (Channels/WebSocket entrypoint)
│   ├── settings.py        # Django project settings
│   ├── urls.py            # Project-level URL routing (REST + WebSocket)
│   └── wsgi.py            # WSGI application (for traditional HTTP servers)
├── manage.py              # Django management script
├── start.py               # Uvicorn entrypoint for ASGI server
├── websocket_test.py      # Example WebSocket client for testing
├── Pipfile                # Python dependencies
├── .gitignore
└── README.md              # (You are here)
```

**Code Flow:**
- HTTP(S) requests are routed via `RIFT/urls.py` to `backend/urls.py` and handled by DRF views in `backend/views.py`.
- WebSocket connections are routed via `RIFT/asgi.py` and `backend/routing.py` to `backend/consumers.py`.
- Data is validated/serialized via `backend/serializers.py` and stored in models from `backend/models.py`.
- Permissions and authentication are enforced via `backend/permissions.py` and JWT.

---

## Key API Endpoints

| Endpoint                                 | Method | Description                                                      |
|-------------------------------------------|--------|------------------------------------------------------------------|
| `/api/device-info/`                      | POST   | Register a new agent device and receive a JWT token              |
| `/api/device-info/`                      | GET    | List all registered devices (user role)                          |
| `/api/device-info/<hardware_id>`         | GET    | Retrieve details for a specific device                           |
| `/api/device-info/<hardware_id>`         | PATCH  | Update details for a specific device                             |
| `/api/<hardware_id>/passwords/`          | GET    | Retrieve passwords for a device                                  |
| `/api/<hardware_id>/passwords/`          | POST   | Submit passwords for a device (agent role)                       |
| `/api/<hardware_id>/history/`            | GET    | Retrieve browser history for a device                            |
| `/api/<hardware_id>/history/`            | POST   | Submit browser history for a device (agent role)                 |
| `/api/<hardware_id>/screenshots/`        | GET    | Retrieve screenshots for a device                                |
| `/api/<hardware_id>/screenshots/`        | POST   | Submit screenshots for a device (agent role)                     |
| `/api/passwords/`                        | POST   | Submit passwords (agent role, no device context)                 |
| `/api/history/`                          | POST   | Submit history (agent role, no device context)                   |
| `/api/screenshots/`                      | POST   | Submit screenshots (agent role, no device context)               |
| `/api/token/`                            | POST   | Obtain JWT access/refresh tokens (login)                         |
| `/api/token/refresh/`                    | POST   | Refresh JWT access token                                         |
| `/api/register/`                         | POST   | Register a new user account                                      |
| `/api/login/`                            | POST   | Login and receive JWT tokens                                     |
| `/ws/`                                   | WS     | WebSocket endpoint for agent communication (see below)           |
| `/swagger/`                              | GET    | Swagger UI for API documentation                                 |

**WebSocket API** (`/ws/`):
- Supports agent authentication, command execution, file system operations, keylogger data, screenshot requests, and more.
- See [`backend/consumers.py`](backend/consumers.py) for all supported message types and formats.

---

## Tech Stack

- **Python 3.11**
- **Django 5.x**
- **Django REST Framework**
- **Django Channels** (WebSocket support)
- **MySQL** (default; can be adapted to PostgreSQL with manual changes in `settings.py`)
- **JWT Authentication** (`djangorestframework-simplejwt`)
- **Swagger/OpenAPI** (`drf-yasg`)
- **CORS** (`django-cors-headers`)
- **Uvicorn** (ASGI server)
- **Docker** & **Nginx** (recommended for production, not included in this repo)

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- Pipenv (recommended) or pip
- MySQL server (or adapt to PostgreSQL with manual changes in `settings.py`)
- (Optional) Docker & Docker Compose

### 1. Clone the Repository

```sh
git clone <repository_url>
cd RIFT---Backend
```

### 2. Install Dependencies

```sh
pipenv install
# or
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root. Example:

```
SECRET_KEY=your-secret-key
DEBUG=True
MYSQL_DATABASE=RIFT_db
MYSQL_USER=RIFT_user
MYSQL_PASSWORD=yourpassword
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

> **Note:**  
> If you want to use PostgreSQL, you must update the `DATABASES` setting in `RIFT/settings.py` accordingly.

### 4. Run Database Migrations

```sh
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (Optional)

```sh
python manage.py createsuperuser
```

### 6. Run the Development Server

For HTTP + WebSocket support (ASGI):

```sh
pipenv shell
python start.py
# or directly:
uvicorn RIFT.asgi:application --host 0.0.0.0 --port 8000 --reload
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) for the API and [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/) for documentation.

---

## Usage Instructions

- **REST API:** Use any HTTP client (curl, Postman, frontend) to interact with `/api/` endpoints.
- **WebSocket:** Connect agents or test clients to `ws://localhost:8000/ws/`.
  - Example test client: [`websocket_test.py`](websocket_test.py)
- **Admin Panel:** Access at `/admin/` with superuser credentials.
- **Swagger UI:** Explore and test APIs at `/swagger/`.

---

## Contribution Guidelines

Contributions are welcome! To contribute:

1. Fork this repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests where appropriate.
4. Commit and push: `git commit -am 'Add new feature'`
5. Open a pull request with a clear description.

---

## License

This project is licensed under the MIT License.

---

## Disclaimer

**Project RIFT** is developed strictly for educational and ethical cybersecurity research purposes. Unauthorized deployment, use, or distribution of this tool against systems you do not own or have explicit permission to test is strictly prohibited and may be illegal. The author assumes no liability for misuse.

---