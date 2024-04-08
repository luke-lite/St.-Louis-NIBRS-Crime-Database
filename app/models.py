from typing import Optional
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class UploadInfo(db.Model):
    __tablename__ = 'upload_info'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    upload_date: so.Mapped[datetime.date] = so.mapped_column(sa.Date(), index=True)
    month: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    year: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    filename: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)

    def __repr__(self):
        return '<Filename: {}>'.format(self.filename)
    
class CrimeData(db.Model):
    __tablename__ = 'crime_data'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    IncidentNum: so.Mapped[int] = so.mapped_column(sa.Integer(), index=True)
    IncidentDate: so.Mapped[datetime.date] = so.mapped_column(sa.Date(), index=True)
    TimeOccurred: so.Mapped[datetime.time] = so.mapped_column(sa.DateTime(), index=True)
    SLMPDOffense: so.Mapped[str] = so.mapped_column(sa.String(240))
    NIBRSCode: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    NIBRSCat: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    NIBRSOffenseType: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    UCR_SRS: so.Mapped[float] = so.mapped_column(sa.Float())
    # grades: 'f' felony, 'm' misdemeanor, 'c' citation, 'i' infraction
    CrimeGrade: so.Mapped[str] = so.mapped_column(sa.String(64))
    PrimaryLocation: so.Mapped[str] = so.mapped_column(sa.String(120))
    SecondaryLocation: so.Mapped[str] = so.mapped_column(sa.String(120))
    District: so.Mapped[float] = so.mapped_column(sa.String(120), index=True)
    Neighborhood: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    NeighborhoodNum: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    Latitude: so.Mapped[float] = so.mapped_column(sa.Float())
    Longitude: so.Mapped[float] = so.mapped_column(sa.Float())
    Supplemented: so.Mapped[bool] = so.mapped_column(sa.Boolean(), index=True)
    SupplementDate: so.Mapped[datetime.date] = so.mapped_column(sa.Date(), index=True)
    VictimNum: so.Mapped[float] = so.mapped_column(sa.Float(), index=True)
    FirearmUsed: so.Mapped[bool] = so.mapped_column(sa.Boolean(), index=True)
    IncidentNature: so.Mapped[str] = so.mapped_column(sa.String(240), index=True)

    def __repr__(self):
        return '<Incident Number: {}>'.format(self.IncidentNum)