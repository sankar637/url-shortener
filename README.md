# URL Shortener API

A FastAPI project for creating and resolving shortened URLs.

## Project structure

```text
url-shortener-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── utils.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and adjust the values as needed.

## Run

Start the development server from the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive documentation is available at `/docs`.
