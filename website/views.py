from flask import Blueprint, render_template, request, redirect, flash, send_from_directory, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, Artikel, Uitlening
from datetime import datetime
import pandas as pd
from itertools import groupby
from operator import attrgetter


views = Blueprint('views', __name__)

# Routes

@views.route('/reserved_dates')
def reserved_dates():
    uitleningen = Uitlening.query.all()
    reserved_dates_dict = {}
    for uitlening in uitleningen:
        if uitlening.artikel_id not in reserved_dates_dict:
            reserved_dates_dict[uitlening.artikel_id] = []

        # geneerd de datums 
        date_range = pd.date_range(start=uitlening.start_date, end=uitlening.end_date)
        for date in date_range:
            reserved_dates_dict[uitlening.artikel_id].append(date.strftime('%Y-%m-%d'))  # format date as string

    return jsonify(reserved_dates_dict)

# Homepagina/Catalogus
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # Bepalen welke form is ingediend
        formNaam = request.form.get('form_name')

        # Formulier om items te filteren/sorteren
        if formNaam == 'sorteer':
            sortItems = request.form.get('AZ')
            
            # Alle geselecteerde categorieën en merken ophalen uit het formulier
            selected_categories = request.form.getlist('category')
            selected_merk = request.form.getlist('merk')
            
            #standaard query
            query = Artikel.query
            
            if 'All' not in selected_categories:
                query = Artikel.query.filter(Artikel.category.in_(selected_categories))
                
            if 'All' not in selected_merk:
                query = Artikel.query.filter(Artikel.merk.in_(selected_merk))

            # Alphabetisch sorteren op verschillende manieren
            if sortItems == 'AZ':
                artikels = query.order_by(Artikel.title).all()
            elif sortItems == 'ZA':
                artikels = query.order_by(Artikel.title.desc()).all()
            else:
                artikels = query.all()

            grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}

            return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)
        

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
                if startDatum.weekday() >= 5 or eindDatum.weekday() >= 5:
                    raise ValueError('Reservatie is niet toegestaan op zaterdag of zondag')
                elif current_user.type_id == 2 and (eindDatum - startDatum).days > 7:
                    raise ValueError('Reservatie is niet toegestaan voor studenten langer dan 7 dagen')
                new_uitlening = Uitlening(user_id = current_user.id, artikel_id = artikelid, start_date = startDatum, end_date = eindDatum)
                artikel = Artikel.query.get_or_404(artikelid)
                artikel.user_id = current_user.id
                db.session.add(new_uitlening)
                db.session.commit()
                flash('Reservatie gelukt.', category='success')
                return redirect('/')
            except ValueError:
                flash('Ongeldige datum', category='error') 
                return redirect('/') 
            except:
                flash('Reservatie mislukt.', category='error')
                return redirect('/')
    
        
        
        
    
    artikels = Artikel.query
    grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}

    return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)
    

#Zorgt ervoor dat images geladen kunnen worden
@views.route('images/<path:filename>')
def get_image(filename):
    return send_from_directory('images', filename)



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