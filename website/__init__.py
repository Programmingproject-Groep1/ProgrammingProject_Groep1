# Init bestand: hier wordt de app geïnitialiseerd en de database gecreëerd.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
import csv
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from datetime import datetime, timedelta


db = SQLAlchemy()
DB_NAME = "databank.db"

# Functie om de app te creëren
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'programmingproject'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    

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

    create_database(app)
    upload_csv(app, Artikel)
    create_user(app, User)
    
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
    student = User(email = "student@test", first_name = "student", password= generate_password_hash("password", method='pbkdf2:sha256'), type_id = 2, type_int = 0, waarschuwing = 0, blacklist_end_date = None)
    admin = User(email = "admin@test", first_name = "admin", password= generate_password_hash("password", method='pbkdf2:sha256'), type_id = 1, type_int = 0, waarschuwing = 0, blacklist_end_date = None)
    docent = User(email = "docent@test", first_name = "docent", password= generate_password_hash("password", method='pbkdf2:sha256'), type_id = 3, type_int = 0, waarschuwing = 0, blacklist_end_date = None)
    with app.app_context():
        db.session.add(admin)
        db.session.add(student)
        db.session.add(docent)
        db.session.commit()
    


# Functie die het CSV bestand inleest en de data in de databank steekt
def upload_csv(app, Artikel):
    csv_file_path = 'Uitleendienst-inventaris.csv'
    if os.path.exists(csv_file_path):
        try:
            with open(csv_file_path, 'r') as file:
                csv_data = csv.reader(file, delimiter=',')
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

# Functie die checkt of artikels te laat zijn elke keer dat de app opstart en of de blacklist termijn van alle gebruikers voorbij is



def check_telaat(app, Uitlening, Artikel, User):
    with app.app_context():
        uitleningen = Uitlening.query.all()
        for uitlening in uitleningen:
            if uitlening.end_date < datetime.now().date() and uitlening.actief:
                artikel = Artikel.query.filter_by(id=uitlening.artikel_id).first()
                uitlening.user.waarschuwing += 1
                if uitlening.user.waarschuwing >= 2:
                    uitlening.user.type_int = 1
                    uitlening.user.blacklist_end_date = datetime.now() + timedelta(days=90)
                    uitlening.user.waarschuwing = 0
                db.session.commit()
                print(f"Artikel {artikel.title} is te laat en is teruggebracht")
        print("Te laat en blacklist check uitgevoerd")
        users = User.query.all()
        for user in users:
            if user.blacklist_end_date and user.blacklist_end_date < datetime.now() and user.type_int == 1:
                user.type_int = 0
                db.session.commit()
                print(f"Gebruiker {user.first_name} is niet meer op de blacklist")
        












