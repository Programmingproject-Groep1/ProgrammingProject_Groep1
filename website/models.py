from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Artikel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merk = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    nummer = db.Column(db.Integer)
    category = db.Column(db.String(50))
    beschrijving = db.Column(db.String(150))
    afbeelding = db.Column(db.String(150), nullable=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    reserveringen = db.relationship('Artikel')