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
├── backend/             # FastAPI Logic (Python 3.14)
│   ├── app/
│   │   ├── main.py      # Entry point
│   │   ├── auth.py      # JWT & Login logic
│   │   └── database.py  # Connections to Postgres/Mongo
│   └── Dockerfile
├── frontend/            # Svelte 5 (Port 7999)
│   ├── src/
│   └── Dockerfile
└── docker-compose.yml   # Orchestrates the containers

```
---

# 🛠️ Environment Setup & Installation

This project is built using the latest features of Python 3.14 and SvelteKit. It is assumed that Python 3.14 is already installed on your system.

## Backend Setup (FastAPI)

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

## Frontend Setup (SvelteKit)

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


## Database & Orchestration

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
docker-compose up --build

```

* **Frontend:** Access the UI at `http://localhost:7999`
* **Backend:** Access the API docs at `http://localhost:8000/docs`

---

## 🔑 Security (Authentication)

We use **JWT (JSON Web Tokens)** to keep your data safe.

1. **Login:** You provide your credentials to the `/login` endpoint.
2. **Key:** If correct, the server gives your browser a "Digital Key" (the Token).
3. **Permissions:** When you try to view or change a document, the server checks your key against the **PostgreSQL** records to make sure you have permission to access that specific version.

---

## 🛡️ License

This project is licensed under the **GNU General Public License version 3 (GPLv3)**.
