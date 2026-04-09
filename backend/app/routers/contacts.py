import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.models.database import get_db
from app.models.contact import Contact, ContactList

router = APIRouter()


class ContactCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tags: Optional[list[str]] = []
    list_id: Optional[int] = None


class ContactListCreate(BaseModel):
    name: str
    description: Optional[str] = None


@router.post("/lists")
async def create_list(req: ContactListCreate, db: Session = Depends(get_db)):
    contact_list = ContactList(name=req.name, description=req.description)
    db.add(contact_list)
    db.commit()
    db.refresh(contact_list)
    return {"id": contact_list.id, "name": contact_list.name}


@router.get("/lists")
async def get_lists(db: Session = Depends(get_db)):
    lists = db.query(ContactList).all()
    return [
        {"id": cl.id, "name": cl.name, "description": cl.description, "created_at": str(cl.created_at)}
        for cl in lists
    ]


@router.post("")
async def add_contact(req: ContactCreate, db: Session = Depends(get_db)):
    contact = Contact(
        name=req.name,
        email=req.email,
        phone=req.phone,
        tags=req.tags,
        list_id=req.list_id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return {"id": contact.id, "name": contact.name, "email": contact.email}


@router.post("/import")
async def import_contacts(
    file: UploadFile = File(...),
    list_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported")

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    imported = 0
    for row in reader:
        contact = Contact(
            name=row.get("name", ""),
            email=row.get("email", ""),
            phone=row.get("phone", ""),
            tags=row.get("tags", "").split(";") if row.get("tags") else [],
            list_id=list_id,
        )
        db.add(contact)
        imported += 1

    db.commit()
    return {"imported": imported, "list_id": list_id}


@router.get("")
async def list_contacts(
    list_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Contact)
    if list_id:
        query = query.filter(Contact.list_id == list_id)

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "tags": c.tags,
                "subscribed": c.subscribed,
                "list_id": c.list_id,
            }
            for c in items
        ],
    }


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(404, "Contact not found")
    db.delete(contact)
    db.commit()
    return {"deleted": True}
