import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import URL
from .schemas import URLCreate, URLResponse
from .utils import generate_short_code


# Load environment variables
load_dotenv()


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="URL Shortener API",
    description="A URL Shortener API built using FastAPI and PostgreSQL.",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://url-shortener-gamma-wheat.vercel.app",
        "https://url-shortener-theta-topaz.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Base URL
# --------------------------------------------------

BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost:8000"
)


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "URL Shortener API is running",
        "docs": "/docs"
    }


# --------------------------------------------------
# Create Short URL
# --------------------------------------------------

@app.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED
)
def shorten_url(
    url_data: URLCreate,
    db: Session = Depends(get_db)
):
    original_url = str(url_data.url)

    # Generate a unique short code
    while True:
        short_code = generate_short_code()

        existing_url = (
            db.query(URL)
            .filter(URL.short_code == short_code)
            .first()
        )

        if not existing_url:
            break

    # Create database record
    new_url = URL(
        original_url=original_url,
        short_code=short_code
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    # Create complete short URL
    short_url = f"{BASE_URL}/{short_code}"

    return {
        "short_code": short_code,
        "short_url": short_url
    }


# --------------------------------------------------
# Get URL History
# --------------------------------------------------

@app.get("/urls")
def get_urls(
    db: Session = Depends(get_db)
):
    urls = (
        db.query(URL)
        .order_by(URL.created_at.desc())
        .all()
    )

    return [
        {
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "short_url": f"{BASE_URL}/{url.short_code}",
            "created_at": url.created_at
        }
        for url in urls
    ]


# --------------------------------------------------
# Delete Short URL
# --------------------------------------------------

@app.delete("/urls/{url_id}")
def delete_url(
    url_id: int,
    db: Session = Depends(get_db)
):
    url_record = (
        db.query(URL)
        .filter(URL.id == url_id)
        .first()
    )

    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    db.delete(url_record)
    db.commit()

    return {
        "message": "URL deleted successfully"
    }


# --------------------------------------------------
# Redirect Short URL
# --------------------------------------------------

@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    db: Session = Depends(get_db)
):
    url_record = (
        db.query(URL)
        .filter(URL.short_code == short_code)
        .first()
    )

    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )

    return RedirectResponse(
        url=url_record.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )