"""Bramka demo: rejestracja odwiedzającego (publiczna) i lista dla admina (+ CSV)."""
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import demo_visitors as svc
from .. import visitor_activity, visitor_notify
from ..config import settings
from ..database import get_db
from ..deps import AdminOnly as admin_only
from ..exports import csv_safe
from ..models import DemoVisitor, User
from .portal import public_rate_limit

router = APIRouter(prefix="/api", tags=["demo-visitors"])


class VisitorIn(BaseModel):
    first_name: str
    last_name: str
    company: str
    consent: bool = False
    website: str = ""   # honeypot — człowiek go nie widzi i nie wypełnia

    @field_validator("first_name", "last_name", "company")
    @classmethod
    def _clean(cls, value: str) -> str:
        return svc.clean_field(value)


@router.post("/public/demo-visitor", status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(public_rate_limit)])
def register_visitor(body: VisitorIn, response: Response, db: Session = Depends(get_db)):
    if body.website.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nieprawidłowe zgłoszenie.")
    if not body.consent:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Zgoda na informację o przetwarzaniu danych jest wymagana.")
    _, token = svc.register(db, body.first_name, body.last_name, body.company)
    visitor_notify.notify_visitor(body.first_name, body.last_name, body.company)
    response.set_cookie(svc.VISITOR_COOKIE, token, max_age=svc.COOKIE_DAYS * 86400,
                        httponly=True, samesite="lax", secure=settings.secure_cookies)


class ViewIn(BaseModel):
    path: str = Field(max_length=300)


@router.post("/public/demo-visitor/view", status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(public_rate_limit)])
def record_view(body: ViewIn, request: Request, db: Session = Depends(get_db)):
    """Sygnał z frontu przy zmianie ekranu na koncie demo; liczy tylko gościa z ważnym ciasteczkiem.

    Zawsze 204 (bez zdradzania, czy coś zaliczono); błąd zapisu = tylko log."""
    visitor_activity.record_view(db, request.cookies.get(svc.VISITOR_COOKIE), body.path)


def _rows(db: Session) -> list[DemoVisitor]:
    return list(db.scalars(select(DemoVisitor).order_by(DemoVisitor.created_at.desc(),
                                                         DemoVisitor.id.desc()).limit(5000)))


@router.get("/admin/demo-visitors")
def list_visitors(db: Session = Depends(get_db), user: User = admin_only):
    return [{"id": v.id, "first_name": v.first_name, "last_name": v.last_name,
             "company": v.company, "created_at": v.created_at.isoformat(),
             "page_views": v.page_views or 0,
             "last_seen_at": v.last_seen_at.isoformat() if v.last_seen_at else None,
             "duration_min": visitor_activity.duration_min(v),
             "top_sections": visitor_activity.top_sections(v)} for v in _rows(db)]


@router.get("/admin/demo-visitors.csv")
def export_visitors(db: Session = Depends(get_db), user: User = admin_only):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["data", "imie", "nazwisko", "firma", "ekrany", "czas_min", "najczesciej"])
    for v in _rows(db):
        minutes = visitor_activity.duration_min(v)
        writer.writerow([v.created_at.strftime("%Y-%m-%d %H:%M"), csv_safe(v.first_name),
                         csv_safe(v.last_name), csv_safe(v.company), v.page_views or 0,
                         "" if minutes is None else minutes,
                         csv_safe(", ".join(visitor_activity.top_sections(v)))])
    return StreamingResponse(iter(["﻿" + buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": 'attachment; filename="demo-odwiedzajacy.csv"'})
