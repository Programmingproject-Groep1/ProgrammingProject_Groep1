# Init bestand: hier wordt de app geïnitialiseerd en de database gecreëerd.
from flask import Flask, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from os import path
import os
import csv
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from .config import api_key
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect

#Databank specifieren
db = SQLAlchemy()
DB_NAME = "databank.db"
#Upload folder specifieren
UPLOAD_FOLDER = 'static/schade'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

mail = Mail()

limiter = Limiter(key_func=get_remote_address)



# Functie om de app te creëren
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'programmingproject'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'  
    app.config['MAIL_PORT'] = 587  
    app.config['MAIL_USE_TLS'] = True  
    app.config['MAIL_USERNAME'] = '758401001@smtp-brevo.com'  
    app.config['MAIL_PASSWORD'] = api_key 
    app.config['MAIL_DEFAULT_SENDER'] = 'ehbuitleendienst@gmail.com'

    mail.init_app(app)

    limiter.init_app(app)
    

    csrf = CSRFProtect(app)
    

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Artikel, Uitlening

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    

    #create_database(app)
    #upload_csv(app, Artikel)
    #create_user(app, User)
    #create_uitlening(app, Uitlening)
    
    check_telaat(app, Uitlening, Artikel, User)
    
    return app



# Functie om de database te creëren
def create_database(app):
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            print('Creating Database...')
            db.create_all()
            print('Database Created!')

# Functie om testgebruikers te aan te maken
def create_user(app, User):
    student = User(email = "student@test", first_name = "Student",last_name ="Test1", password= generate_password_hash("password", method='pbkdf2:sha256',  salt_length= 16), type_id = 2, blacklisted = 0, reden_blacklist ="dit is een test", warning = 0, blacklist_end_date = None)
    admin = User(email = "admin@test", first_name = "Admin", last_name ="Test2", password= generate_password_hash("password", method='pbkdf2:sha256',  salt_length= 16), type_id = 1, blacklisted = 0, reden_blacklist ="", warning = 0, blacklist_end_date = None)
    docent = User(email = "docent@test", first_name = "Docent", last_name ="Test3", password= generate_password_hash("password", method='pbkdf2:sha256',  salt_length= 16), type_id = 3, blacklisted = 0, reden_blacklist ="", warning = 0, blacklist_end_date = None)
    student1 = User(email = "student1@test", first_name = "Milan", last_name ="Van Trimpont", password= generate_password_hash("password", method='pbkdf2:sha256',  salt_length= 16), type_id = 2, blacklisted = 1, reden_blacklist ="", warning = 0, blacklist_end_date = datetime(2024, 9, 5))
    student2 = User(email = "student2@test", first_name = "Younes",last_name ="Aki", password= generate_password_hash("password", method='pbkdf2:sha256',  salt_length= 16), type_id = 2, blacklisted = 0, reden_blacklist ="", warning = 0, blacklist_end_date = None)
    with app.app_context():
        db.session.add(admin)
        db.session.add(student)
        db.session.add(docent)
        db.session.add(student1)
        db.session.add(student2)
        db.session.commit()

#Functie om testuitleningen te maken
def create_uitlening(app, Uitlening):
    with app.app_context():
        uitlening = Uitlening(user_id = 1, artikel_id = 1, start_date = datetime(2024, 5, 1), end_date = datetime(2024, 5, 8), actief = 1)
        uitlening1 = Uitlening(user_id = 2, artikel_id = 22, start_date = datetime(2024, 5, 1), end_date = datetime(2024, 5, 26), actief = 1)
        uitlening2 = Uitlening(user_id = 3, artikel_id = 22, start_date = datetime(2024, 6, 3), end_date = datetime(2024, 6, 8), actief = 0)
        uitlening3 = Uitlening(user_id = 4, artikel_id = 4, start_date = datetime(2024, 5, 1), end_date = datetime(2024, 5, 8), actief = 1)
        uitlening4 = Uitlening(user_id = 5, artikel_id = 5, start_date = datetime(2024, 5, 1), end_date = datetime(2024, 5, 8), actief = 1)
        db.session.add(uitlening)
        db.session.add(uitlening1)
        db.session.add(uitlening2)
        db.session.add(uitlening3)
        db.session.add(uitlening4)
        db.session.commit()
    


# Functie die het CSV bestand inleest en de data in de databank steekt
def upload_csv(app, Artikel):
    csv_file_path = 'Uitleendienst-inventaris.csv'
    if os.path.exists(csv_file_path):
        try:
            with open(csv_file_path, 'r') as file:
                csv_data = csv.reader(file, delimiter=';')
                next(csv_data)  
                with app.app_context():  
                    for row in csv_data:
                        if len(row) < 5 :  
                            print(f"Skipping row: {row}")
                            continue
                        Artikel_instance = Artikel(
                            merk=row[0],
                            title=row[1],
                            nummer=int(row[2]) if row[2] !='' else 0,
                            category=row[3],
                            type_product=row[4],
                            beschrijving=row[5],
                            afbeelding=row[6]
                        )
                        db.session.add(Artikel_instance)
                    db.session.commit()
                print("CSV file uploaded successfully!")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("CSV file not found.")



# Functie die checkt of artikels te laat zijn elke keer dat de app opstart en of de blacklist up to date is

def check_telaat(app, Uitlening, Artikel, User):
    with app.app_context():
        uitleningen = Uitlening.query.all() #Alle uitleningen opvragen
        sent_reminders = set() #Set om te checken of er al een herinnering is verstuurd
        for uitlening in uitleningen:
            if uitlening.end_date < datetime.now().date() and uitlening.actief and uitlening.warning == 0: #Als de uitlening te laat is en er nog geen waarschuwing is gegeven
                artikel = Artikel.query.filter_by(id=uitlening.artikel_id).first() #Het artikel van de uitlening die te laat is opvragen
                uitlening.user.warning += 1 #Waarschuwing geven aan de gebruiker
                msg = Message('Waarschuwing', recipients=[uitlening.user.email]) #Melding van de waarschuwing sturen naar de gebruiker
                msg.body = f"Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} nog niet ingeleverd. U heeft nu {uitlening.user.warning} waarschuwing(en). Bij 3 waarschuwingen wordt u op de blacklist gezet.\n\nMet vriendelijke groeten,\n\nEHB Uitleendienst"
                mail.send(msg)
                uitlening.warning = 1
                if uitlening.user.warning >= 2: #Als de gebruiker meer dan 2 waarschuwingen heeft
                    uitlening.user.blacklisted = 1 #Gebruiker op de blacklist zetten voor 3 maanden
                    uitlening.user.blacklist_end_date = datetime.now() + timedelta(days=90)
                    msg = Message('Blacklist', recipients=[uitlening.user.email]) #Mail sturen naar de gebruiker dat hij op de blacklist is gezet
                    msg.body = f"Beste {uitlening.user.first_name},\n\nU bent op de blacklist gezet. U kunt 90 dagen geen artikelen meer uitlenen.\n\nMet vriendelijke groeten,\n\nEHB Uitleendienst"
                    mail.send(msg)
                    uitlening.user.warning = 0
                    uitlening.user.reden_blacklist = "Meer dan 2 keer te laat met inleveren van artikelen"
                    print(f"Gebruiker {uitlening.user.first_name} {uitlening.user.last_name} is op de blacklist gezet")
                db.session.commit()
                print(f"Artikel {artikel.title} is te laat, gebruiker {uitlening.user.first_name} {uitlening.user.last_name} heeft een waarschuwing gekregen")
                volgendeMaandag = datetime.now().date() + timedelta(days=(7 - datetime.now().weekday()))
                #Kijken of er een uitlening is met het zelfde artikelid als de uitlening die te laat is, die volgende week opgehaald moet worden
                conflictUitlening = Uitlening.query.filter(Uitlening.artikel_id == uitlening.artikel_id, Uitlening.start_date == volgendeMaandag).first() 
                if conflictUitlening: #Als er een conflict is, zien of het artikel mogelijks vervangen kan worden door een ander exemplaar van het zelfde artikel dat niet gereserveerd is
                    vervangArtikel  = Artikel.query.filter(Artikel.title == conflictUitlening.artikel.title, Artikel.id != conflictUitlening.artikel.id).all()
                    if vervangArtikel: #Als er een of meerdere mogelijke vervangartikels zijn

                        vervangingGevonden = False #Variabele om te checken of er een vervanging is gevonden
                        for artikel in vervangArtikel: #Voor elk vervangartikel checken of het al is uitgeleend voor volgende week
                            checkMogelijk = Uitlening.query.filter_by(artikel_id = artikel.id).filter(Uitlening.start_date == volgendeMaandag).first()
                            if not checkMogelijk: #Als het artikel niet is uitgeleend voor volgende week, de uitlening vervangen met het nieuwe artikel
                                vervangUitlening = Uitlening(user_id = conflictUitlening.user_id, artikel_id = artikel.id, start_date = conflictUitlening.start_date, end_date = conflictUitlening.end_date, actief = 0)
                                db.session.add(vervangUitlening)
                                db.session.delete(conflictUitlening)
                                db.session.commit()
                                vervangingGevonden = True
                                print(f"Artikel {artikel.id} is vervangen voor artikel {conflictUitlening.artikel.id} voor gebruiker {conflictUitlening.user_id}")
                                break
                        if not vervangingGevonden: #Als er geen vervanging is gevonden, een mail sturen naar de gebruiker dat het artikel niet beschikbaar is en de reservering annuleren
                            msg = Message('Artikel niet beschikbaar', recipients=[conflictUitlening.user.email])
                            msg.body = f"Beste {conflictUitlening.user.first_name},\n\nHet artikel {conflictUitlening.artikel.title} is niet beschikbaar voor volgende week, en er is geen extra exemplaar van dit artikel dat u kan uitlenen. Onze excuses hiervoor.\n\nU zal een mail krijgen wanneer u het artikel weer kan reserveren\n\nMet vriendelijke groeten,\n\nEHB Uitleendienst"
                            mail.send(msg)
                            db.session.delete(conflictUitlening)
                            db.session.commit()
                            print(f"Artikel {conflictUitlening.artikel.title} is niet beschikbaar voor volgende week voor gebruiker {conflictUitlening.user.first_name} {conflictUitlening.user.last_name}")
                    else: #Als er geen vervangartikels zijn, een mail sturen naar de gebruiker dat het artikel niet beschikbaar is en de reservering annuleren
                        msg = Message('Artikel niet beschikbaar', recipients=[conflictUitlening.user.email])
                        msg.body = f"Beste {conflictUitlening.user.first_name},\n\nHet artikel {conflictUitlening.artikel.title} is niet beschikbaar voor volgende week, en er is geen extra exemplaar van dit artikel dat u kan uitlenen. Onze excuses hiervoor.\n\nU zal een mail krijgen wanneer u het artikel weer kan reserveren\n\nMet vriendelijke groeten,\n\nEHB Uitleendienst"
                        mail.send(msg)
                        db.session.delete(conflictUitlening)
                        db.session.commit()
                        print(f"Artikel {conflictUitlening.artikel.title} is niet beschikbaar voor volgende week voor gebruiker {conflictUitlening.user.first_name} {conflictUitlening.user.last_name}")
            elif uitlening.end_date == datetime.now().date() + timedelta(days=1) and uitlening.actief and uitlening.id not in sent_reminders: #Als de uitlening morgen moet worden ingeleverd en er nog geen herinnering is verstuurd
                artikel = Artikel.query.filter_by(id=uitlening.artikel_id).first()
                msg = Message('Herinnering', recipients=[uitlening.user.email]) #Mail sturen naar de gebruiker dat hij het artikel morgen moet inleveren
                msg.body = f"Beste {uitlening.user.first_name},\n\nVergeet niet om het artikel {artikel.title} morgen in te leveren.\n\nMet vriendelijke groeten,\n\nEHB Uitleendienst"
                mail.send(msg)
                print(f"Herinnering voor artikel {artikel.title} is verstuurd naar gebruiker {uitlening.user.first_name} {uitlening.user.last_name}")
        users = User.query.all()
        for user in users: #Voor elke gebruiker checken of de blacklist moet worden opgeheven
            if user.blacklist_end_date and user.blacklist_end_date < datetime.now() and user.blacklisted == 1:
                user.blacklisted = 0
                user.blacklist_end_date = None
                msg = Message('Blacklist', recipients=[user.email]) #Mail sturen naar de gebruiker dat hij niet meer op de blacklist staat
                msg.body = f"Beste {user.first_name},\n\nUw blacklist is opgeheven. U kunt weer artikelen uitlenen.\n\nMet vriendelijke groeten,\n\nEHB Uitleendienst"
                mail.send(msg)
                sent_reminders.add(uitlening.id) 
                db.session.commit()
                print(f"Gebruiker {user.first_name} {user.last_name} is niet meer op de blacklist")
        print("Te laat en blacklist check uitgevoerd") #Bericht dat de check is uitgevoerd
        












