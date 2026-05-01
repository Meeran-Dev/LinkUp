# LinkUp

LinkUp is a real-time messaging web application with:
- FastAPI backend (`server`)
- React + Vite frontend (`client`)
- Redis for pub/sub + presence
- SQL database via SQLAlchemy

## 1. Prerequisites

Install these first:
- **Node.js** 18+ (20+ recommended)
- **Python** 3.10+
- **Redis** (running locally)
- A SQL database (PostgreSQL recommended, SQLite also works for local testing)

## 2. Clone and open project

```bash
git clone <your-repo-url>
cd LinkUp
```

## 3. Backend setup (`server`)

From the project root:

```bash
cd server
python -m venv .venv
```

Activate the virtual environment:

- **Windows (PowerShell)**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **macOS/Linux**
  ```bash
  source .venv/bin/activate
  ```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside `server/` with:

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/linkup
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
```

Notes:
- For SQLite (quick local setup), you can use:
  `DATABASE_URL=sqlite:///./linkup.db`
- `SECRET_KEY` should be a long random string in real deployments.

Run backend API:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend should now be available at `http://127.0.0.1:8000`.

## 4. Frontend setup (`client`)

Open a second terminal from project root:

```bash
cd client
npm install
npm run dev
```

Frontend should now be available at `http://localhost:5173`.

## 5. Running the app

Keep both services running:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`

Open the frontend URL, register a user, and start chatting.

## 6. Useful commands

- Frontend lint:
  ```bash
  cd client && npm run lint
  ```
- Stop backend/frontend:
  - Use `Ctrl + C` in each terminal.
