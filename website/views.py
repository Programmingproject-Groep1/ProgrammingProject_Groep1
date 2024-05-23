from flask import Blueprint, render_template, request, redirect, flash, send_from_directory, jsonify, url_for, request, session
from flask_login import login_user, login_required, logout_user, current_user
from . import db, ALLOWED_EXTENSIONS
from .models import User, Artikel, Uitlening
from datetime import datetime, date, timedelta
import pandas as pd
from itertools import groupby
from operator import attrgetter
from sqlalchemy import cast, Date
from werkzeug.utils import secure_filename
import os



views = Blueprint('views', __name__)

# Routes


#Zorgt ervoor dat de gereserveerde datums van de artikels getoond kunnen worden

@views.route('/reserved_dates')
def reserved_dates():
    uitleningen = Uitlening.query.all()
    reserved_dates_dict = {}
    for uitlening in uitleningen:
        if uitlening.artikel_id not in reserved_dates_dict:
            reserved_dates_dict[uitlening.artikel_id] = []
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


#Bepaalt welke types bestanden geupload mogen worden
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Route naar Infopagina
@views.route("/infopagina")
def infopagina():
    user = current_user
    return render_template('infopagina.html', user= user)

    


# Homepagina/Catalogus
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    #Als de user een admin is
    if current_user.type_id == 1:
        #Bepalen start en einddata van de gekozen week
        vandaag = date.today()
        dagen = (vandaag.weekday() + 7) % 7
        datumbeginweek = vandaag - timedelta(days=dagen)
        datumeindweek = datumbeginweek + timedelta(days=4)
    
        if request.method == 'POST':
            #Als de user op de knop klikt om naar de volgende of vorige week te gaan
            if request.form.get('form_name') == 'nextweek':
                session['weken'] = session.get('weken', 0) + 1
            elif request.form.get('form_name') == 'prevweek':
                session['weken'] = session.get('weken', 0) - 1
            #Als een artikel wordt opgehaald    
            elif request.form.get('form_name') == 'ophalen':
                artikelid = request.form.get('artikelid')
                userid = request.form.get('userid')
                uitlening = Uitlening.query.filter(Uitlening.artikel_id == artikelid, ~Uitlening.actief, Uitlening.return_date == None).first()
                if uitlening and uitlening.user_id == int(userid):
                    uitlening.actief = True
                    db.session.commit()
                    flash('Artikel opgehaald', category='success')
                    redirect('/')
                elif uitlening and uitlening.user_id != int(userid):
                    flash('User-ID behoort niet tot deze uitlening.', category='error')
                elif not uitlening:
                    uitlening = Uitlening(user_id = userid, artikel_id = artikelid, start_date = datumbeginweek, end_date = datumeindweek)
                    uitlening.actief = True
                    db.session.add(uitlening)
                    db.session.commit()
                    flash('Artikel opgehaald', category='success')
                    redirect('/')
            #Als een artikel wordt ingeleverd
            elif request.form.get('form_name') == 'inleveren':
                artikelid = request.form.get('artikelid')
                userid = request.form.get('userid')
                uitlening = Uitlening.query.filter(Uitlening.artikel_id == artikelid, Uitlening.actief).first()
                schade = request.form.get('schade')
                if uitlening and uitlening.user_id == int(userid):
                    #Indien er schade is: Beschrijving van de schade en foto van de schade worden toegevoegd
                    if schade == 'ja':
                        uitlening.schade_beschrijving = request.form.get('schadeBeschrijving')
                        uitlening.actief = False
                        file = request.files['file']
                        uitlening.return_date = date.today()
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file.save(os.path.join('website/static/schade', filename))
                            uitlening.schade_foto = filename
                        db.session.commit()
                        flash('Schade gemeld en artikel ingeleverd.', category='success')
                        
                    else:
                        uitlening.actief = False
                        uitlening.return_date = date.today()
                        db.session.commit()
                        flash('Artikel ingeleverd', category='success')
                elif uitlening and uitlening.user_id != int(userid):
                    flash('User-ID behoort niet tot deze uitlening.', category='error')
                else:
                    flash('Artikel niet gevonden bij uitleningen.', category='error')
                    
            # Als de gebruiker wordt verbannen
            elif request.form.get('form_name') == 'ban':
                user_id = request.form.get('userid')
                user = User.query.get(user_id)
                if user:
                    user.blacklisted = True
                    # Voeg de banperiode toe (3 maanden)
                    user.ban_end_date = datetime.now() + timedelta(days=90)
                    db.session.commit()
                    flash('Gebruiker verbannen voor 3 maanden.', category='success')
                else:
                    flash('Gebruiker niet gevonden.', category='error')

        datumbeginweek += timedelta(days=7 * session.get('weken', 0))
        datumeindweek += timedelta(days=7 * session.get('weken', 0))

        artikelsophaal = Uitlening.query.filter(Uitlening.start_date == datumbeginweek , ~Uitlening.actief, Uitlening.return_date == None).all() 
        artikelsterug = Uitlening.query.filter(Uitlening.end_date == datumeindweek , Uitlening.actief, Uitlening.return_date == None).all() 
        artikelsOvertijd = Uitlening.query.filter(Uitlening.end_date < date.today(), Uitlening.actief, Uitlening.return_date == None).all()
        #Rendert de template voor de admin homepagina    
        return render_template("homeadmin.html", user=current_user, artikelsophaal=artikelsophaal or [], artikelsterug = artikelsterug or [], datumbeginweek = datumbeginweek, datumeindweek= datumeindweek, artikelsOvertijd = artikelsOvertijd or [])
            
    #Als de user een student of docent is
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
                    flash('Reservatie gelukt.', category='modal')
                    artikels = Artikel.query
                    grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}

                    return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)
                except ValueError as e:
                    flash('Ongeldige datum: ' + str(e), category='modalerror') 
                    return redirect('/') 
                except Exception as e:
                    flash('Reservatie mislukt.' + str(e), category='modalerror')
                    return redirect('/')
        
    
        artikels = Artikel.query
        grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}

        return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)
        





@views.route('/adminblacklist', methods=['GET', 'POST'])
@login_required
def admin_blacklist():
    # kijken of de gebruiker een admin is
    if current_user.type_id == 1:
        if request.method == 'POST':
            # kijken of de gebruiker wordt gebanned
            if request.form.get('form_name') == 'ban':
                user_id = request.form.get('userid')
                reden_blacklist = request.form.get('reden_blacklist')
                user = User.query.get(user_id)
                if user:
                    user.blacklisted = True
                    user.reden_blacklist = reden_blacklist
                    # laat de geruiker gebanned worden voor 3 maanden
                    user.blacklist_end_date = datetime.now() + timedelta(days=90)
                    #melding meegeven
                    db.session.commit()
                    flash('Gebruiker verbannen voor 3 maanden.', category='success')
                else:
                    flash('Gebruiker niet gevonden.', category='error')
            # Als de gebruiker wordt geunbaned
            elif request.form.get('form_name') == 'unban':
                user_id = request.form.get('userid')
                user = User.query.get(user_id)
                if user:
                    user.blacklisted = False
                    user.blacklist_end_date = None
                    db.session.commit()
                    flash('Gebruiker is niet langer verbannen.', category='success')
                else:
                    flash('Gebruiker niet gevonden.', category='error')
        
        # Ophalen van alle gebruikers voor de blacklistpagina
        query = User.query
        # Filteren op bannen of niet banned
        filter_option = request.form.get('filteren')
        
        if filter_option == 'all':
            query = User.query
        elif filter_option == 'banned':
            query = query.filter_by(blacklisted=True)
        elif filter_option == 'niet_banned':
            query = query.filter_by(blacklisted=False)
            
        # Alphabetisch sorteren op verschillende manieren
        weergaven = request.form.get('weergaven')
        if weergaven == 'voornaam_az':
            query = query.order_by(User.first_name)
        elif weergaven == 'voornaam_za':
            query = query.order_by(User.first_name.desc())
        elif weergaven == 'naam_az':
            query = query.order_by(User.last_name)
        elif weergaven == 'naam_za':  
            query = query.order_by(User.last_name.desc())
        elif weergaven == 'studentnummer_laag_hoog':
            query = query.order_by(User.id)
        elif weergaven == 'studentnummer_hoog_laag':  
            query = query.order_by(User.id.desc())
                
        users = query.all()
        # Rendert de template voor de blacklistpagina
        return render_template("adminblacklist.html", user=current_user, users=users, filter_option=filter_option, weergaven=weergaven)
        
        
        
#Zorgt ervoor dat images geladen kunnen worden
@views.route('images/<path:filename>')
def get_image(filename):
    return send_from_directory('images', filename)

#Route naar artikelbeheer
@views.route('/adminartikels',methods=['GET', 'POST'])
def artikelbeheer():
    artikels = Artikel.query.all()
    user = current_user
    
    # Als het formulier wordt ingediend
    if request.method == 'POST':
        # Controleer of de ID van de bewerkte kaart is doorgegeven
        editable_id = request.form.get('editable_id')
        
        # Als het formulier wordt ingediend om wijzigingen op te slaan
        if 'save' in request.form:
            # Loop door elk artikel in het formulier
            for artikel in artikels:
                if str(artikel.id) == editable_id:
                    # Controleer of er gegevens zijn gewijzigd voor dit artikel
                    if (request.form.get(f"title_{editable_id}") != artikel.title or
                        request.form.get(f"merk_{editable_id}") != artikel.merk or
                        request.form.get(f"nummer_{editable_id}") != artikel.nummer or
                        request.form.get(f"category_{editable_id}") != artikel.category):
                        
                        # Update de gegevens in de database
                        artikel.title = request.form.get(f"title_{editable_id}")
                        artikel.merk = request.form.get(f"merk_{editable_id}")
                        artikel.nummer = request.form.get(f"nummer_{editable_id}")
                        artikel.category = request.form.get(f"category_{editable_id}")
                        db.session.commit()

            # Redirect naar dezelfde pagina om de geüpdatete gegevens te tonen
            return redirect(url_for('views.artikelbeheer'))

    # Als het een GET-verzoek is of als het formulier wordt ingediend om te bewerken
    editable_id = request.args.get('editable_id')
    editable = bool(editable_id)

    return render_template('adminartikels.html', artikels=artikels, user=user, editable=editable, editable_id=editable_id)


#route naar additem en toevoegen van product
@views.route('/additem', methods=['GET', 'POST'])
def additem():
    if request.method == 'POST':
        #data halen uit van de admin
        merk = request.form['merk']
        title = request.form['title']
        nummer = request.form['nummer']
        category = request.form['category']
        beschrijving = request.form['beschrijving']
        #nog afbeelding toevoegen

        #een artikel object aanmaken
        new_Artikel = Artikel(
            merk = merk,
            title = title,
            nummer = nummer,
            category = category,
            beschrijving = beschrijving,
            #nog afbeelding toevoegen   
        )
        try:
            #nieuwe artikel aan de database toevoegen
            db.session.add(new_Artikel)
            db.session.commit()
            flash('Artikel succesvol toegevoegd')
            return redirect(url_for('index'))
        except Exception as e:
            #kijkt na als de admin fout info toevoegt
             flash('Fout van het toevoegen van artikel {e}' , 'danger')
             return redirect(url_for('additem'))

    artikels = Artikel.query.all()
    users = current_user 
    return render_template('additem.html', artikels = artikels, users=users)



#Pagina waar user zijn reserveringen kan bekijken
@views.route('/userartikels')
@login_required
def reservaties():
    uitleningen_actief = Uitlening.query.filter(Uitlening.user_id == current_user.id, Uitlening.actief).all()
    uitleningen = Uitlening.query.filter(Uitlening.user_id == current_user.id, Uitlening.actief == False).all()
    uitlening_teruggebracht = Uitlening.query.filter(Uitlening.user_id == current_user.id, Uitlening.actief == False, Uitlening.return_date != None).all()
    artikels = Artikel.query.filter(Artikel.id.in_([uitlening.artikel_id for uitlening in uitleningen])).all()
    return render_template('userartikels.html', uitleningen=uitleningen, user=current_user, artikels=artikels, uitleningen_actief=uitleningen_actief, uitlening_teruggebracht=uitlening_teruggebracht)

#Route om artikel te verlengen
@views.route('/verleng/<int:id>', methods=['GET', 'PUT'])
def verleng(id):
    uitlening = Uitlening.query.get_or_404(id)
    if (uitlening.verlengd == False):
        uitlening.end_date += timedelta(days=7)
        uitlening.verlengd = True
        db.session.commit()
        flash('Artikel verlengd.', category='success')
        return redirect('/userartikels')
    
    while (uitlening.verlengd == True):
        flash('Artikel kan niet verlengd worden.', category='error')
        return redirect('/userartikels')
    

#Route om een reservatie te annuleren
@views.route('/verwijder/<int:id>', methods=['GET', 'PUT'])
def verwijder(id):
    uitlening = Uitlening.query.get_or_404(id)

    try:
        uitlening.artikel.user_id = None
        db.session.delete(uitlening)
        db.session.commit()
        flash('Reservatie geannuleerd.', category='normal')
        return redirect('/userartikels')
    except:
        flash('Reservatie verwijderen mislukt.', category='error')
        return redirect('/userartikels')


