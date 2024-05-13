from flask import Blueprint, render_template, request, redirect, flash, send_from_directory, jsonify, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, Artikel, Uitlening
from datetime import datetime, date, timedelta
import pandas as pd
from itertools import groupby
from operator import attrgetter
from sqlalchemy import cast, Date
from flask_dropzone import Dropzone
import os



views = Blueprint('views', __name__)

# Routes




@views.route('/reserved_dates')
def reserved_dates():
    uitleningen = Uitlening.query.all()
    reserved_dates_dict = {}
    #today = datetime.today()
    #start_date = uitlening.start_date
    #end_date = min(start_date + timedelta(days=6), uitlening.end_date)

    for uitlening in uitleningen:
       # if uitlening.start_date > today + timedelta(days=14):
       #     continue 
        if uitlening.artikel_id not in reserved_dates_dict:
            reserved_dates_dict[uitlening.artikel_id] = []

        # genereerd de datums 
        date_range = pd.date_range(start=uitlening.start_date, end=uitlening.end_date)
        for date in date_range:
            reserved_dates_dict[uitlening.artikel_id].append(date.strftime('%Y-%m-%d'))  # format date as string

    return jsonify(reserved_dates_dict)

#Zorgt dat artikel getoond kan worden bij invoeren van id in admin dashboard
@views.route('/get-artikel')
def get_artikel():
    id = request.args.get('id')
    artikel = Artikel.query.get(id)
    if Artikel is None:
        return jsonify(error='Artikel bestaat niet'), 404
    
    afbeelding_url = url_for('static', filename=f'images/{artikel.afbeelding}')
    return jsonify(title = artikel.title, afbeelding = afbeelding_url)



# Homepagina/Catalogus
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if current_user.type_id == 1:
        vandaag = date.today()
        dagen = (vandaag.weekday() + 7) % 7
        datumbeginweek = vandaag - timedelta(days=dagen)
        datumeindweek = datumbeginweek + timedelta(days=4)
        artikelsophaal = Uitlening.query.filter(Uitlening.start_date == datumbeginweek).all() 
        artikelsterug = Uitlening.query.filter(Uitlening.end_date == datumeindweek).all() 
        if request.method == 'POST':
            if request.form.get('form_name') == 'nextweek':
                datumbeginweek += timedelta(days=7)
                datumeindweek += timedelta(days=7)
                artikelsophaal = Uitlening.query.filter(Uitlening.start_date == datumbeginweek).all() 
                artikelsterug = Uitlening.query.filter(Uitlening.end_date == datumeindweek).all()
                

            elif request.form.get('form_name') == 'prevweek':
                datumbeginweek -= timedelta(days=7)
                datumeindweek -= timedelta(days=7)
                artikelsophaal = Uitlening.query.filter(Uitlening.start_date == datumbeginweek).all() 
                artikelsterug = Uitlening.query.filter(Uitlening.end_date == datumeindweek).all()
            
            elif request.form.get('form_name') == 'inleveren':
                artikelid = request.form.get('artikelid')
                userid = request.form.get('userid')
                uitlening = Uitlening.query.filter(Uitlening.artikel_id == artikelid).first()
                schade = request.form.get('schade')
                if uitlening and uitlening.user_id == int(userid):
                    if schade == 'ja':
                        uitlening.schade_beschrijving = request.form.get('schade_beschrijving')
                        uitlening.actief = False
                        db.session.commit()
                        flash('Schade gemeld en artikel ingeleverd.', category='success')
                        for key, f in request.files.items():
                            if key.startswith('dropzone'):
                                f.save(os.path.join('website/static/schade', f.filename))
                                uitlening.schade_foto = f.filename
                                db.session.commit()
                                flash('Schade foto geupload.', category='success')
                    else:
                        uitlening.actief = False
                        db.session.commit()
                        flash('Artikel ingeleverd', category='success')
                elif uitlening and uitlening.user_id != int(userid):
                    flash('User-ID behoort niet tot deze uitlening.', category='error')
                else:
                    flash('Artikel niet gevonden bij uitleningen.', category='error')
            
        return render_template("homeadmin.html", user=current_user, artikelsophaal=artikelsophaal or [], artikelsterug = artikelsterug or [], datumbeginweek = datumbeginweek, datumeindweek= datumeindweek)
            
    
    elif current_user.type_id == 3 or current_user.type_id == 2:
        if request.method == 'POST':
            # Bepalen welke form is ingediend
            formNaam = request.form.get('form_name')

            # Formulier om items te filteren/sorteren
            if formNaam == 'sorteer':
                sortItems = request.form.get('AZ')
            
            # Alle geselecteerde categorieën en merken ophalen uit het formulier
                selected_categories = request.form.getlist('category')
                selected_merk = request.form.getlist('merk')
                selected_type = request.form.getlist('Type_product')
            
            #standaard query
                query = Artikel.query
            
                if selected_categories:
                    query = query.filter(Artikel.category.in_(selected_categories))
        
                # filteren op merk
                if selected_merk:
                    query = query.filter(Artikel.merk.in_(selected_merk))
                
                #filteren op type product
                if selected_type:
                    query = query.filter(Artikel.type_product.in_(selected_type))
                
          
            # Alphabetisch sorteren op verschillende manieren
                if sortItems == 'AZ':
                    query = query.order_by(Artikel.title)
                elif sortItems == 'ZA':
                    query = query.order_by(Artikel.title.desc())
                
                artikels = query

                grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}
                # Geselecteerde categorieën, merken en sortering behouden in de template
                return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels, selected_categories=selected_categories, selected_merk=selected_merk, selected_type=selected_type, sortItems=sortItems)

                #Formulier om items te zoeken op naam
            elif formNaam == 'search':
                search = request.form.get('search')
                artikels = Artikel.query.filter(Artikel.title.like(f'%{search}%')).all()
                grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}

                return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)
            #Formulier om items te reserveren
            elif formNaam == 'reserveer':
                datums = request.form.get('datepicker').split(' to ')
                artikelid = request.form.get('artikel_id')
            
                try:
                    startDatum = datetime.strptime(datums[0], '%Y-%m-%d')
                    eindDatum = datetime.strptime(datums[1], '%Y-%m-%d')
                    if startDatum.weekday() != 0 or eindDatum.weekday() != 4:
                        raise ValueError('Afhalen is alleen mogelijk op maandag en terugbrengen op vrijdag')
                    elif current_user.type_id == 2 and (eindDatum - startDatum).days > 5:
                        raise ValueError('Reservatie voor studenten kan maximum 5 dagen lang zijn')
                    elif current_user.type_id == 2 and (startDatum - datetime.today()).days > 14:
                        raise ValueError('Studenten kunnen pas 14 dagen op voorhand reserveren')
                    new_uitlening = Uitlening(user_id = current_user.id, artikel_id = artikelid, start_date = startDatum, end_date = eindDatum)
                    artikel = Artikel.query.get_or_404(artikelid)
                    artikel.user_id = current_user.id
                    db.session.add(new_uitlening)
                    db.session.commit()
                    flash('Reservatie gelukt.', category='success')
                    return redirect('/')
                except ValueError as e:
                    flash('Ongeldige datum: ' + str(e), category='error') 
                    return redirect('/') 
                except Exception as e:
                    flash('Reservatie mislukt.' + str(e), category='error')
                    return redirect('/')
        
    
        artikels = Artikel.query
        grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}

        return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)
    





#Blacklist pagina admin
@views.route('/adminblacklist', methods=['GET', 'POST'])
def blacklist():
    users = User.query 

    if request.method == 'POST':
        blacklisted = request.form.get('blacklisted')
        if blacklisted == 0:
            users = User.query.filter_by(blacklisted == False)
            
    return render_template("adminblacklist.html", user=current_user, users=users)
#Zorgt ervoor dat images geladen kunnen worden
@views.route('images/<path:filename>')
def get_image(filename):
    return send_from_directory('images', filename)

#Route naar artikelbeheer
@views.route('/artikelbeheer')
def artikelbeheer():
    artikels = Artikel.query
    user = current_user
    return render_template('adminartikels.html', artikels = artikels, user= user)

#Pagina waar user zijn reserveringen kan bekijken
@views.route('/userartikels')
@login_required
def reservaties():
    uitleningen = Uitlening.query.filter_by(user_id = current_user.id).all()
    artikels = Artikel.query.filter(Artikel.id.in_([uitlening.artikel_id for uitlening in uitleningen])).all()
    return render_template('userartikels.html', uitleningen = uitleningen, user=current_user, artikels = artikels)

#Route om een reservatie te annuleren
@views.route('/verwijder/<int:id>', methods=['GET', 'PUT'])
def verwijder(id):
    uitlening = Uitlening.query.get_or_404(id)

    try:
        uitlening.artikel.user_id = None
        db.session.delete(uitlening)
        db.session.commit()
        return redirect('/userartikels')
    except:
        flash('Reservatie verwijderen mislukt.', category='error')
        return redirect('/userartikels')


# if request.method == 'POST':
    #     #Bepalen welke form is ingediend
    #     formName = request.form.get('form_name')
    #     #Formulier om items te filteren/sorteren
    #     if formName == 'sorteer':
    #         sortItems = request.form.get('AZ')
    #         category = request.form.get('category')

    #         if category == 'All':
    #             query = Artikel.query
    #         else:
    #             query = Artikel.query.filter_by(category=category)

    #         if sortItems == 'AZ':
    #             artikels = query.order_by(Artikel.title).all()
    #         elif sortItems == 'ZA':
    #             artikels = query.order_by(Artikel.title.desc()).all()
    #         else:
    #             artikels = query.all()

    #         grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}

    #         return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)