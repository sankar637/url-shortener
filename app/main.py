import os

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import URL
from .schemas import URLCreate, URLResponse, URLHistoryResponse
from .utils import generate_short_code


# Create database tables
Base.metadata.create_all(bind=engine)


# FastAPI application
app = FastAPI(
    title="URL Shortener API",
    description="URL Shortener API built using FastAPI and PostgreSQL.",
    version="2.0.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost:8000"
)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "URL Shortener API is running",
        "docs": "/docs"
    }


# ---------------------------------------------------------
# Create Short URL
# ---------------------------------------------------------

@app.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED
)
def shorten_url(
    url_data: URLCreate,
    db: Session = Depends(get_db)
):
    """
    Create a shortened URL.
    """

    original_url = str(url_data.url)

    # Generate unique short code
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
        short_code=short_code,
        click_count=0
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    short_url = f"{BASE_URL}/{short_code}"

    return {
        "short_code": short_code,
        "short_url": short_url
    }


# ---------------------------------------------------------
# URL History
# ---------------------------------------------------------

@app.get(
    "/urls",
    response_model=list[URLHistoryResponse]
)
def get_urls(
    search: str | None = Query(
        default=None,
        description="Search by original URL or short code"
    ),
    db: Session = Depends(get_db)
):
    """
    Get URL history.
    Supports search.
    """

    query = db.query(URL)

    if search:
        search_value = f"%{search}%"

        query = query.filter(
            (URL.original_url.ilike(search_value))
            |
            (URL.short_code.ilike(search_value))
        )

    urls = (
        query
        .order_by(URL.created_at.desc())
        .all()
    )

    result = []

    for url in urls:

        result.append({
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "short_url": f"{BASE_URL}/{url.short_code}",
            "created_at": url.created_at,
            "click_count": url.click_count
        })

    return result


# ---------------------------------------------------------
# Delete URL
# ---------------------------------------------------------

@app.delete("/urls/{url_id}")
def delete_url(
    url_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a shortened URL.
    """

    url = (
        db.query(URL)
        .filter(URL.id == url_id)
        .first()
    )

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    db.delete(url)
    db.commit()

    return {
        "message": "URL deleted successfully"
    }


# ---------------------------------------------------------
# Redirect Short URL
# ---------------------------------------------------------

@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Redirect short URL to original URL
    and increase click count.
    """

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

    # Increase visit count
    url_record.click_count += 1

    db.commit()

    return RedirectResponse(
        url=url_record.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )