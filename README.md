# Bulk Certificate Generator

## Running the Application

### Backend
The backend runs on FastAPI and SQLite.

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Start the server (runs on port 8000 by default)
python -m uvicorn --app-dir backend app.main:app --reload
```

### Frontend
The frontend is a React + TypeScript application using Vite and Tailwind CSS.

```bash
cd frontend

# Install dependencies
npm install

# Start the development server (runs on port 5173 by default)
npm run dev

# Build for production
npm run build
```

*Note: The backend has CORS configured to permit `http://localhost:5173` and `http://127.0.0.1:5173`.*

### Testing

The backend includes a fully isolated `pytest` automated test suite.

```bash
# Ensure the virtual environment is activated

# On Windows (PowerShell):
$env:PYTHONPATH="backend"; python -m pytest backend/tests -v

# On Mac/Linux:
PYTHONPATH="backend" python -m pytest backend/tests -v
```
