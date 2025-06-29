from typing import List

from sqlalchemy import select, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactModel
from datetime import date, timedelta


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int) -> List[Contact]:
        stmt = select(Contact).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            contact.first_name = body.first_name
            contact.last_name = body.last_name
            contact.birthday = body.birthday
            contact.email = body.email
            contact.phone = body.phone
            contact.note = body.note
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def search_contacts(
        self, skip: int, limit: int, first_name: str, last_name: str, email: str
    ) -> List[Contact]:
        stmt = (
            select(Contact)
            .filter(
                or_(Contact.first_name == first_name, first_name is None),
                or_(Contact.last_name == last_name, last_name is None),
                or_(Contact.email == email, email is None),
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_birthdays(self, skip: int, limit: int) -> List[Contact]:
        date_beg = date.today()
        date_end = date_beg + timedelta(days=7)
        month_day_beg = date_beg.month * 100 + date_beg.day
        month_day_end = date_end.month * 100 + date_end.day
        stmt = (
            select(Contact)
            .filter(
                extract("month", Contact.birthday) * 100
                + extract("day", Contact.birthday)
                >= month_day_beg,
                extract("month", Contact.birthday) * 100
                + extract("day", Contact.birthday)
                <= month_day_end,
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
