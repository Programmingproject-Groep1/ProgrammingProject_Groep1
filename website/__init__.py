from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
import csv
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "databank.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'programmingproject'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Artikel

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    #create_database(app)
    #upload_csv(app, Artikel)

    return app

def create_database(app):
    with app.app_context():
        if not path.exists('website/' + DB_NAME):
            print('Creating Database...')
            db.create_all()
            print('Database Created!')
    



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
                            beschrijving=row[4],
                            afbeelding=row[5]
                        )
                        db.session.add(Artikel_instance)
                    db.session.commit()
                print("CSV file uploaded successfully!")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("CSV file not found.")















