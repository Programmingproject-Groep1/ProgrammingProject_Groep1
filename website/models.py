from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Databankmodellen

#Tabel voor de artikelen
class Artikel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merk = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    nummer = db.Column(db.Integer)
    category = db.Column(db.String(50))
    type_product = db.Column(db.String(50))
    beschrijving = db.Column(db.String(150))
    afbeelding = db.Column(db.String(150), nullable=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'))

#Tabel voor de gebruikers
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    type_id = db.Column(db.Integer)
    blacklisted = db.Column(db.Boolean, default=False)
    waarschuwing = db.Column(db.Integer, default=0)
    blacklist_end_date = db.Column(db.DateTime, nullable=True)
    reserveringen = db.relationship('Artikel')

#Tabel voor de uitleningen
class Uitlening(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    artikel_id = db.Column(db.Integer, db.ForeignKey('artikel.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    verlengd = db.Column(db.Boolean, default=False)
    actief = db.Column(db.Boolean, default=False)
    schade_beschrijving = db.Column(db.String(150))
    schade_foto = db.Column(db.String(150))
    artikel = db.relationship('Artikel')
    user = db.relationship('User')