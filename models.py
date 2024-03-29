# from sqlalchemy.orm import validates
# from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
# from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
# import random 


from config import db, bcrypt
# from cryptography.fernet import Fernet


class Uploads(db.Model, SerializerMixin):
    # using specific table names for now
    __tablename__ = 'uploads_table'

    id = db.Column(db.Integer, primary_key=True)
    upload_date = db.Column(db.DateTime, default=datetime.now())
    month = db.Column(db.String(20))
    year = db.Column(db.Integer)
    filename = db.Column(db.String(100))

    def __repr__(self):
        return f'<Uploads {self.id}>'