from typing import Optional
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class UploadInfo(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    upload_date: so.Mapped[datetime.date] = so.mapped_column(sa.Date(), index=True)
    month: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    year: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    filename: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True, index=True)

    def __repr__(self):
        return '<Filename: {}>'.format(self.filename)