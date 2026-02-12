# 👁️ IzanagiDB

<p align="center">
  <img src="images_for_documentation/IzanagiDB_logo.png" alt="IzanagiDB Logo" width="200">
</p>

**IzanagiDB** is a tool that lets you save different versions of your document. Instead of just overwriting a file, it saves every change you make.

Think of it like **"Undo/Redo" for your database**. You can look back at what a document looked like yesterday, see exactly what words were changed, and "rewind" back to a previous version if you make a mistake.

### Why two databases?

We use a **Hybrid Setup** because different databases are good at different things:

1. **PostgreSQL (The Librarian):** It keeps track of the "Who, When, and Where." It knows which user made a change and when they did it.
2. **MongoDB (The Warehouse):** It stores the actual content. Since your data might change shape (adding new fields), MongoDB is flexible enough to store it without breaking.

---

## 🛠️ The Stack

* **Backend:** FastAPI (**Python 3.14**) - Handles the logic and talks to the databases.
* **Frontend:** **Svelte 5** - The user interface (Port 7999).
* **Database A:** **PostgreSQL** - Stores user accounts and the history list.
* **Database B:** **MongoDB** - Stores the actual document data and the changes (deltas).
* **Tools:** **Docker** - Connects everything through a private virtual network.

---

## 🏗️ How it works (Docker Networking)

Inside the Docker network, the apps talk to each other using internal names. Your Python code connects to `db` for Postgres and `nosql` for Mongo. This keeps the databases private and secure from the outside world.

---

## 📂 Project Structure

```text
IzanagiDB/
├── .gitignore
├── README.md
├── Design_Roadmap.md            # How I reasoned on system design
├── docker-compose.yml           # Orchestrates all services
├── generate_keys.py             # Generates RSA keys for JWT
├── python_requirements.txt      # Python dependencies
│
├── backend/
│   ├── Dockerfile               # Backend container definition
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app entry point + CORS
│       ├── config.py            # Environment variables & settings
│       ├── database.py          # PostgreSQL & MongoDB connections
│       ├── tables.py            # SQLAlchemy ORM models
│       ├── schemas.py           # Pydantic validation schemas
│       ├── auth.py              # JWT & password hashing logic
│       ├── dependencies.py      # JWT authentication dependency
│       ├── create_databases.sql # Database schema (for reference, not used)
│       └── routes/
│           ├── __init__.py
│           ├── auth.py          # /auth endpoints (login, register, etc.)
│           └── documents.py     # /documents endpoints (CRUD, versions)
│
└── frontend/
    ├── Dockerfile               # Frontend container definition
    ├── package.json             # Node dependencies
    ├── package-lock.json
    ├── vite.config.ts           # Vite config (port 7999)
    ├── svelte.config.js         # SvelteKit config
    ├── tsconfig.json            # TypeScript config
    ├── .prettierrc              # Code formatting
    ├── .prettierignore
    ├── .npmrc
    ├── .gitignore
    ├── README.md
    │
    ├── static/
    │   └── robots.txt
    │
    └── src/
        ├── app.html              # HTML template
        ├── app.d.ts              # TypeScript declarations
        ├── lib/
        │   ├── index.ts
        │   ├── styles.css        # Global CSS variables & fonts
        │   ├── assets/
        │   │   └── favicon.svg
        │   └── components/
        │       └── Nav.svelte    # Navigation component
        │
        └── routes/
            ├── +page.svelte      # Home page (/)
            ├── +layout.svelte    # Global layout with Nav
            │
            ├── auth/
            │   └── +page.svelte  # Login/Signup page (/auth)
            │
            └── documents/
                ├── +page.svelte  # Document list (/documents)
                └── [id]/
                    └── +page.svelte  # Document viewer/editor (/documents/[id])
```
---

## 🛠️ Environment Setup & Installation

This project is built using the latest features of Python 3.14 and SvelteKit. It is assumed that Python 3.14 is already installed on your system.

---

### Environment Configuration

The backend requires environment variables for database connections and JWT authentication. The `.env` file is gitignored, so add one of your own, whose content looks like this:

```Bash
POSTGRES_HOST=postgre
POSTGRES_PORT=5432
POSTGRES_USER=izanagi_user
POSTGRES_PASSWORD=izanagi_pass
POSTGRES_DB=izanagi_db

MONGO_HOST=mongo
MONGO_PORT=27017

# JWT Configuration
JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
```

### Backend Setup (FastAPI)

We use a dedicated virtual environment to manage dependencies and ensure version consistency.

1. Create the Virtual Environment:

Navigate to the backend/ directory and create an environment named `izanagi_venv`:

```Bash
python3.14 -m venv izanagi_venv
```

2. Activate the Environment:
```Bash
source izanagi_venv/bin/activate  # Linux/macOS
izanagi_venv\Scripts\activate     # Windows 
```

3. Install Core Libraries:

```Bash
pip install -r python_requirements.txt
```

### Generate JWT RSA Keys

IzanagiDB uses RS256 (RSA asymmetric encryption) for JWT tokens. You need to generate a private/public key pair before starting the backend. These keys will be saved in `backend/` directory, but their paths are added in `.gitignore`. Simply run:

```Bash
cd backend/app
python3.14 ../../generate_keys.py
```

### Frontend Setup (SvelteKit)

SvelteKit acts as the modern framework for our Svelte 5 components. It manages routing and communicates with the FastAPI backend via API calls.

1. Initialize SvelteKit:

If you are starting the `frontend/` folder from scratch, use the following command to bootstrap a SvelteKit Minimal project with TypeScript and Prettier:

```Bash
npx sv create --template minimal --types ts --add prettier --install npm frontend
```

2. Install Dependencies:

After the project is created, navigate to the `frontend/` directory and install the text-diffing library required for the document version viewer:

```Bash
cd frontend
npm install diff
```

3. Configure API Proxying:

To avoid CORS issues during development, ensure your SvelteKit `fetch` calls point to the FastAPI default port (`http://localhost:8000`).


### Database & Orchestration

Since IzanagiDB relies on a hybrid database approach, the easiest way to get the environment ready is through Docker, as defined in the `docker-compose.yml`.

1. Verify Docker Installation: Ensure Docker and Docker Compose are running.

2. Launch the Stack:

```Bash
docker-compose up --build
```

This command pulls the official images for PostgreSQL and MongoDB, sets up the internal network, and starts your Python and SvelteKit services simultaneously.


---

## 🚀 How to Start

To launch the entire system (Databases, Backend, and Frontend), run the following command in your terminal:

```bash
docker-compose down && docker-compose up --build

```

* **Frontend:** Access the UI at `http://localhost:7999`
* **Backend:** Access the API docs at `http://localhost:8000/docs`

---

## 🛡️ License

This project is licensed under the **GNU General Public License version 3 (GPLv3)**.
