from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

# Base abstract class
class CrimeDataBase(db.Model):
    __abstract__ = True

    Id: so.Mapped[int] = so.mapped_column(sa.Integer(), primary_key=True)
    IncidentNum: so.Mapped[int] = so.mapped_column(sa.Integer(), index=True)
    IncidentDate: so.Mapped[datetime.date] = so.mapped_column(sa.Date(), index=True, nullable=True)
    TimeOccurred: so.Mapped[datetime.time] = so.mapped_column(sa.DateTime(), index=True, nullable=True)
    SLMPDOffense: so.Mapped[str] = so.mapped_column(sa.String(240), nullable=True)
    NIBRSCode: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, nullable=True)
    NIBRSCat: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, nullable=True)
    NIBRSOffenseType: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, nullable=True)
    SRS_UCR: so.Mapped[float] = so.mapped_column(sa.Float(), nullable=True)
    CrimeGrade: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=True)
    PrimaryLocation: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=True)
    SecondaryLocation: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=True)
    District: so.Mapped[float] = so.mapped_column(sa.String(120), index=True, nullable=True)
    Neighborhood: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, nullable=True)
    NeighborhoodNum: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, nullable=True)
    Latitude: so.Mapped[float] = so.mapped_column(sa.Float(), nullable=True)
    Longitude: so.Mapped[float] = so.mapped_column(sa.Float(), nullable=True)
    Supplemented: so.Mapped[bool] = so.mapped_column(sa.Boolean(), index=True, nullable=True)
    SupplementDate: so.Mapped[datetime.date] = so.mapped_column(sa.Date(), index=True, nullable=True)
    VictimNum: so.Mapped[float] = so.mapped_column(sa.Float(), index=True, nullable=True)
    FirearmUsed: so.Mapped[bool] = so.mapped_column(sa.Boolean(), index=True, nullable=True)
    IncidentNature: so.Mapped[str] = so.mapped_column(sa.String(240), index=True, nullable=True)

class MetaData(db.Model):
    __tablename__ = 'meta_data'

    Idx: so.Mapped[int] = so.mapped_column(sa.Integer(), primary_key=True)
    LastUpdated: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=True)

# Existing static models
class CrimeData(CrimeDataBase):
    __tablename__ = 'crime_data'

class UnfoundedCrimeData(CrimeDataBase):
    __tablename__ = 'unfounded_data'

class RawCrimeData(CrimeDataBase):
    __tablename__ = 'raw_data'

    DatePublished: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=True)