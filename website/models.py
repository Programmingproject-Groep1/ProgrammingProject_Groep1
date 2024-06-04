from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Databankmodellen

#Tabel voor de artikelen
class Artikel(db.Model):
    id = db.Column(db.Integer, primary_key=True) #Unieke artikel-id
    merk = db.Column(db.String(50), nullable=False) #Merk van het artikel
    title = db.Column(db.String(100), nullable=False) #Naam van het artikel
    nummer = db.Column(db.Integer) #Nummer van het artikel(Als er meerdere zijn)
    category = db.Column(db.String(50)) #Categorie van het artikel
    type_product = db.Column(db.String(50)) #Type artikel
    beschrijving = db.Column(db.String(150)) #Beschrijving van het artikel
    afbeelding = db.Column(db.String(150), nullable=True) #Filename afbeelding
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id')) #User die het artikel heeft gereserveerd
    actief = db.Column(db.Boolean, default=True) #Is het artikel zichtbaar

#Tabel voor de gebruikers
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #Unieke user-id
    email = db.Column(db.String(150), unique=True) #Email van de gebruiker
    phone_number = db.Column(db.String(150)) #Telefoonnummer van de gebruiker
    password = db.Column(db.String(150)) #Wachtwoord van de gebruiker(Gehashed)
    first_name = db.Column(db.String(150)) #Voornaam van de gebruiker
    last_name = db.Column(db.String(150)) #Achternaam van de gebruiker
    profile_picture = db.Column(db.String(150), default='profielfotoDummy.jpg') #Profielfoto van de gebruiker
    type_id = db.Column(db.Integer) #Type gebruiker
    blacklisted = db.Column(db.Boolean, default=False) #Is de gebruiker geband
    reden_blacklist = db.Column(db.Text, nullable=True) #Reden van de ban
    warning = db.Column(db.Integer, default=0) #Aantal waarschuwingen
    blacklist_end_date = db.Column(db.DateTime, nullable=True) #Einddatum van de ban
    reserveringen = db.relationship('Artikel') #Artikelen die de gebruiker heeft gereserveerd
    

#Tabel voor de uitleningen
class Uitlening(db.Model):
    id = db.Column(db.Integer, primary_key=True) #Unieke uitlening-id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #User die het artikel heeft geleend
    artikel_id = db.Column(db.Integer, db.ForeignKey('artikel.id')) #Artikel dat is geleend
    start_date = db.Column(db.Date) #Startdatum van de uitlening
    end_date = db.Column(db.Date) #Einddatum van de uitlening
    return_date = db.Column(db.Date) #Datum van terugbrengen
    verlengd = db.Column(db.Boolean, default=False) #Is de uitlening verlengd
    actief = db.Column(db.Boolean, default=False) #Is de uitlening actief
    schade_beschrijving = db.Column(db.String(150)) #Beschrijving van de schade
    schade_foto = db.Column(db.String(150)) #Foto van de schade
    warning_sent = db.Column(db.Integer, default=0) #Is er een waarschuwing gestuurd
    reminder_sent = db.Column(db.Integer, default=0) #Is er een herinnering gestuurd
    artikel = db.relationship('Artikel') #Artikel dat is geleend
    user = db.relationship('User') #User die het artikel heeft geleend