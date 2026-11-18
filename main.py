import random
import string
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Url

#import os
#print("RUNNING FILE:", os.path.abspath(__file__))

app = FastAPI()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# urls = {}

#Base.metadata.create_all(bind=engine)

class UrlRequest(BaseModel):
    url: HttpUrl

    # print("BaseModel:", BaseModel)
    # print("HttpUrl:", HttpUrl)
    # print("Annotations:", __annotations__)

def generate_short_code():
        characters = string.ascii_letters + string.digits
        return "".join([random.choice(characters) for _ in range(6)])

def generate_unique_short_code(db: Session):
    for _ in range(10):
        short_code = generate_short_code()

        # if short_code not in urls:
        #     return short_code
        # while short_code in urls:
        #     short_code = generate_short_code()

        existing_url = db.scalar(
            select(Url).where(Url.short_code == short_code)
        )

        if existing_url is None:
            return short_code

    raise HTTPException(
        status_code=500,
        detail="Unable to generate unique short code",
    )

@app.get("/")
def home():
    return {
        "message": "URL Shortener API"
    }

@app.post("/urls")
def create_url(
    request: UrlRequest,
    db: Session = Depends(get_db),
):
    short_code = generate_unique_short_code(db)
    # urls[short_code] = str(request.url)
    original_url = str(request.url)
    url_record = Url(
        original_url=original_url,
        short_code=short_code,
    )

    db.add(url_record)
    db.commit()
    db.refresh(url_record)

    short_url = f"http://localhost:8000/{short_code}"

    # return {
    #     "original_url": request.url,
    #     "short_code": short_code,
    #     "short_url": short_url,
    # }
    return {
        "id": url_record.id,
        "original_url": url_record.original_url,
        "short_code": url_record.short_code,
        "short_url": short_url,
    }

@app.get("/urls")
def list_url(db: Session = Depends(get_db)):
    url_records = db.scalars(
        select(Url).order_by(Url.id.desc())
    ).all()

    return [
        {
            "id": url_record.id,
            "original_url": url_record.original_url,
            "short_code": url_record.short_code,
            "short_url": f"http://localhost:8000/{url_record.short_code}",
            "visit_count": url_record.visit_count,
        }
        for url_record in url_records
    ]

@app.get("/{short_code}")
def redirect_url(
    short_code: str,
    db: Session = Depends(get_db),
):
    # original_url = urls.get(short_code)
    url_record = db.scalar(
        select(Url).where(Url.short_code == short_code)
    )

    # if original_url is None:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="Short URL not found",
    #     )
    # return RedirectResponse(url=original_url)

    if url_record is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found",
        )

    url_record.visit_count += 1
    db.commit()

    return RedirectResponse(url=url_record.original_url)

@app.delete("/urls/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(
    short_code: str,
    db: Session = Depends(get_db)
):
    url_record = db.scalar(
        select(Url).where(Url.short_code == short_code)
    )

    if url_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    db.delete(url_record)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
