from flask import Blueprint, app, render_template, request, redirect, flash, send_from_directory, jsonify, url_for, request, session
from flask_login import login_user, login_required, logout_user, current_user
from . import db, ALLOWED_EXTENSIONS, mail
from .models import User, Artikel, Uitlening
from datetime import datetime, date, timedelta
import pandas as pd
from itertools import groupby
from operator import attrgetter
from sqlalchemy import cast, Date, or_, and_
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from dateutil import parser
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
        return jsonify(modalerror='Artikel bestaat niet'), 404
    
    afbeelding_url = url_for('static', filename=f'images/{artikel.afbeelding}')
    return jsonify(title = artikel.title, afbeelding = afbeelding_url)


#Zorgt dat user getoond kan worden bij invoeren van id in admin dashboard
@views.route('/get-user')
def get_user():
    id = request.args.get('id')
    user = User.query.get(id)
    if user is None:
        return jsonify(modalerror='User bestaat niet'), 404
   
    
    return jsonify(user = (user.first_name + " " + user.last_name))



#Bepaalt welke types bestanden geupload mogen worden
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Checken of er verboden tekens in de input zitten (Bescherming tegen injection)
def check_input(input):
    if any(char in input for char in ['<', '>', "'", '"', '%', '(', ')', '{', '}', '[', ']', '=', '+', '*', '/', '\\', '|', '&', '^', '$', '#', '!', '?', ':', ';', ',']):
        flash('Ongeldige invoer: verboden tekens', category='modalerror')
        return False
    return True


#Route naar Infopagina
@views.route("/infopagina")
def infopagina():
    user = current_user
    return render_template('infopagina.html', user= user)

#Route naar historiek
@views.route("/historiek")
def historiek():
    user = current_user
    uitleningen = Uitlening.query
    return render_template('historiek.html', user= user, uitleningen = uitleningen)

    


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
        huidigeWeek = False
    
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
                if not artikelid or not userid:
                    flash('Geen artikel of user-ID ingevoerd.', category='modalerror')
                    return redirect('/')
                uitlening = Uitlening.query.filter(Uitlening.artikel_id == artikelid, Uitlening.return_date == None).first()
                if uitlening and uitlening.actief:
                    flash('Artikel is al opgehaald.', category='modalerror')
                elif uitlening and uitlening.user_id == int(userid):
                    uitlening.actief = True
                    db.session.commit()
                    flash('Artikel opgehaald', category='modal')
                    msg = Message('Artikel opgehaald', recipients=[uitlening.user.email])
                    msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} opgehaald.\n\nDeze reservering loopt van: {uitlening.start_date} tot {uitlening.end_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                    mail.send(msg)
                    redirect('/')
                elif uitlening and uitlening.user_id != int(userid):
                    flash('User-ID behoort niet tot deze uitlening.', category='modalerror')
                elif not uitlening:
                    uitlening = Uitlening(user_id = userid, artikel_id = artikelid, start_date = datumbeginweek, end_date = datumeindweek)
                    uitlening.actief = True
                    db.session.add(uitlening)
                    db.session.commit()
                    msg = Message('Artikel opgehaald', recipients=[uitlening.user.email])
                    msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} opgehaald.\n\nDeze reservering loopt van: {uitlening.start_date} tot {uitlening.end_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                    mail.send(msg)
                    flash('Artikel opgehaald', category='modal')
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
                        msg = Message('Artikel ingeleverd', recipients=[uitlening.user.email])
                        msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} ingeleverd op: {uitlening.return_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                        mail.send(msg)
                        flash('Schade gemeld en artikel ingeleverd.', category='modal')
                        
                    else:
                        uitlening.actief = False
                        uitlening.return_date = date.today()
                        msg = Message('Artikel ingeleverd', recipients=[uitlening.user.email])
                        msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} ingeleverd op: {uitlening.return_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                        mail.send(msg)
                        db.session.commit()
                        flash('Artikel ingeleverd', category='modal')
                elif uitlening and uitlening.user_id != int(userid):
                    flash('User-ID behoort niet tot deze uitlening.', category='modalerror')
                else:
                    flash('Artikel niet gevonden bij uitleningen.', category='modalerror')
                    
            # Als de gebruiker wordt verbannen
            elif request.form.get('form_name') == 'reset_week':
                return redirect('/')
        elif request.method == 'GET':
            session['weken'] = 0

        datumbeginweek += timedelta(days=7 * session.get('weken', 0))
        datumeindweek += timedelta(days=7 * session.get('weken', 0))

        if datumbeginweek == (date.today() - timedelta(days=(date.today().weekday() + 7) % 7)):
            huidigeWeek = True

        artikelsophaal = Uitlening.query.filter(Uitlening.start_date >= datumbeginweek , ~Uitlening.actief, Uitlening.return_date == None, Uitlening.start_date <= datumeindweek).all() 
        artikelsterug = Uitlening.query.filter(Uitlening.end_date <= datumeindweek , Uitlening.actief, Uitlening.return_date == None, Uitlening.end_date >= datumbeginweek).all() 
        artikelsOvertijd = Uitlening.query.filter(Uitlening.end_date < date.today(), Uitlening.actief, Uitlening.return_date == None).all()
        #Rendert de template voor de admin homepagina    
        return render_template("homeadmin.html", user=current_user, artikelsophaal=artikelsophaal or [], artikelsterug = artikelsterug or [], datumbeginweek = datumbeginweek, datumeindweek= datumeindweek, artikelsOvertijd = artikelsOvertijd or [], huidigeWeek = huidigeWeek)
            
    #Als de user een student of docent is
    elif current_user.type_id == 3 or current_user.type_id == 2:
        if request.method == 'POST':
            # Bepalen welke form is ingediend
            artikels = Artikel.query.filter_by(actief=True).all()
            formNaam = request.form.get('form_name')

            # Formulier om items te filteren/sorteren
            if formNaam == 'sorteer':
                sortItems = request.form.get('AZ')
            
            # Alle geselecteerde categorieën en merken ophalen uit het formulier
                selected_categories = request.form.getlist('category')
                selected_merk = request.form.getlist('merk')
                selected_type = request.form.getlist('Type_product')

                datums = request.form.get('datums').split(' to ')

                begindatum = datetime.strptime(datums[0], '%Y-%m-%d')
                einddatum = datetime.strptime(datums[1], '%Y-%m-%d')
                
            #standaard query
                query = Artikel.query.filter_by(actief=True)  # Alleen actieve artikelen
                query = query.outerjoin(Uitlening, Artikel.id == Uitlening.artikel_id)
            
                if selected_categories and len(selected_categories) > 0:
                    artikels = Artikel.query.filter(Artikel.category.in_(selected_categories))
        
                # filteren op merk
                if selected_merk and len(selected_merk) > 0:
                    artikels = Artikel.query.filter(Artikel.merk.in_(selected_merk))
                
                #filteren op type product
                if selected_type and len(selected_type) > 0:
                    artikels = Artikel.query.filter(Artikel.type_product.in_(selected_type))

                
                #voeg een filter toe om enkel tussen de begin en einddatum te zoeken
                if begindatum and einddatum:
                    subquery = db.session.query(Uitlening.artikel_id).filter(
                    or_(
                    and_(Uitlening.start_date <= einddatum, Uitlening.end_date >= begindatum),
                    and_(Uitlening.start_date.is_(None), Uitlening.end_date.is_(None))
                        )
                    ).subquery()

                    query = query.filter(~Artikel.id.in_(subquery))

                    
            # Alphabetisch sorteren op verschillende manieren
                if sortItems == 'AZ':
                    query = query.order_by(Artikel.title)
                elif sortItems == 'ZA':
                    query = query.order_by(Artikel.title.desc())
                
                artikels = query.all()

                grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}
                
                # Geselecteerde categorieën, merken en sortering behouden in de template
                return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels, selected_categories=selected_categories,
                                                    selected_merk=selected_merk, selected_type=selected_type, sortItems=sortItems,begindatum=begindatum,einddatum=einddatum)


                #Formulier om items te zoeken op naam
            elif formNaam == 'search':
                search = request.form.get('search')
                if any(char in search for char in ['<', '>', "'", '"']):
                    flash('Ongeldige invoer: verboden tekens', category='modalmodalerror')
                else: 
                    artikels = Artikel.query.filter(Artikel.title.like(f'%{search}%'), Artikel.actief == True).all()
                   

                    grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}
                    return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)
                
            #Formulier om items te reserveren
            elif formNaam == 'reserveer':
                if current_user.blacklisted:
                    flash('Je bent geband en kan geen artikelen reserveren.', category='modalmodalerror')
                    return redirect('/')
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
                    msg = Message('Reservering bevestigd', recipients=[new_uitlening.user.email])
                    msg.body = f'Beste {new_uitlening.user.first_name},\n\nHierbij bevestigen we de reservering van het artikel: {new_uitlening.artikel.title}\n\nDe reservering loopt van {new_uitlening.start_date} tot {new_uitlening.end_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                    mail.send(msg)
                    artikels = Artikel.query
                    grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}

                    return render_template("home.html", user=current_user, artikels=artikels, grouped_artikels=grouped_artikels)
                except ValueError as e:
                    flash('Ongeldige datum: ' + str(e), category='modalerror') 
                    return redirect('/') 
                except Exception as e:
                    flash('Reservering mislukt.' + str(e), category='modalerror')
                    return redirect('/')
        
    
        artikels = Artikel.query.filter_by(actief=True).all()
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
                    flash('Gebruiker verbannen voor 3 maanden.', category='modal')
                else:
                    flash('Gebruiker niet gevonden.', category='modalerror')
            # Als de gebruiker wordt geunbaned
            elif request.form.get('form_name') == 'unban':
                user_id = request.form.get('userid')
                user = User.query.get(user_id)
                if user:
                    user.blacklisted = False
                    user.blacklist_end_date = None
                    db.session.commit()
                    flash('Gebruiker is niet langer verbannen.', category='modal')
                else:
                    flash('Gebruiker niet gevonden.', category='modalerror')

            # Als de ADMIN de gebruiker_type wil wijzigen
            elif request.form.get('form_name') == 'change_type':
                user_id = request.form.get('user_id')
                new_type_id = request.form.get('type_gebruiker')  # verander 'type_id' naar 'type_gebruiker'
                user = User.query.get(user_id)
                if user:
                    user.type_id = int(new_type_id)
                    db.session.commit()
                    flash('Gebruikerstype succesvol gewijzigd.', category='success')
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
@views.route('/adminartikels', methods=['GET', 'POST'])
def artikelbeheer():
    artikels = Artikel.query.all()
    
    user = current_user
    if request.method == 'POST':
        formNaam = request.form.get('form_name')
        if formNaam == 'sorteer':
            sortItems = request.form.get('AZ')
            selected_categories = request.form.getlist('category')
            selected_merk = request.form.getlist('merk')
            selected_type = request.form.getlist('Type_product')

            query = Artikel.query.outerjoin(Uitlening, Artikel.id == Uitlening.artikel_id)

            # Filteren op categorie
            if selected_categories:
                query = query.filter(Artikel.category.in_(selected_categories))

            # Filteren op merk
            if selected_merk:
                query = query.filter(Artikel.merk.in_(selected_merk))

            # Filteren op type product
            if selected_type:
                query = query.filter(Artikel.type_product.in_(selected_type))

            # Alfabetisch sorteren
            if sortItems == 'AZ':
                query = query.order_by(Artikel.title)
            elif sortItems == 'ZA':
                query = query.order_by(Artikel.title.desc())

            artikels = query.all()

            return render_template('adminartikels.html', artikels=artikels, user=user, sortItems=sortItems,
                                   selected_categories=selected_categories, selected_merk=selected_merk, selected_type=selected_type)

                                  
        
        elif formNaam == 'search':
            search = request.form.get('search')
            if any(char in search for char in ['<', '>', "'", '"']):
                flash('Ongeldige invoer: verboden tekens', category='modalerror')
            else:
                artikels = Artikel.query.filter(Artikel.title.like(f'%{search}%')).all()
                grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}
                return render_template('adminartikels.html', artikels=artikels,
                                        user=user, grouped_artikels=grouped_artikels)
        
    # Als het formulier wordt ingediend
    if request.method == 'POST':
        if 'save' in request.form:
            artikelId = request.form.get('id')
            artikel = Artikel.query.get(artikelId)
            if artikel:
                file = request.files["afbeelding_" + str(artikel.id)]
                title = request.form.get("titleInput")
                merk = request.form.get("merkInput")
                category = request.form.get("categoryInput")
                description = request.form.get("descriptionInput")
                

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join('website/static/images', filename))
                    artikel.afbeelding = filename
                    artikel.title = title
                    artikel.merk = merk
                    artikel.category = category
                    artikel.beschrijving = description
                    artikel.actief = not artikel.actief
                    db.session.commit()
                    flash('Artikel succesvol gewijzigd', category='modal')
                elif not file:
                    artikel.title = title
                    artikel.merk = merk
                    artikel.category = category
                    artikel.beschrijving = description
                    artikel.actief = not artikel.actief
                    db.session.commit()
                    flash('Artikel succesvol gewijzigd', category='modal')
                else:
                    flash('Ongeldige afbeelding', category='modalerror')
            else:
                flash('Artikel niet gevonden', category='modalerror')
            return redirect(url_for('views.artikelbeheer'))
        elif 'delete' in request.form:
            artikelId = request.form.get('id')
            artikel = Artikel.query.get(artikelId)
            if artikel:
                db.session.delete(artikel)
                db.session.commit()
                flash('Artikel succesvol verwijderd', category='modal')
            else:
                flash('Artikel niet gevonden', category='modalerror')
            return redirect(url_for('views.artikelbeheer'))

    return render_template('adminartikels.html', artikels=artikels, user=user,)
        

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
        #afbeelding bewerken
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('website/static/images', filename))
            new_Artikel = Artikel(
            merk = merk,
            title = title,
            nummer = nummer,
            category = category,
            beschrijving = beschrijving,
            afbeelding = filename,
        )
        else:
            print("Geen foto")
            new_Artikel = Artikel(
            merk = merk,
            title = title,
            nummer = nummer,
            category = category,
            beschrijving = beschrijving,
            
        ) 
        #een artikel object aanmaken
        
        try:
            #nieuwe artikel aan de database toevoegen
            db.session.add(new_Artikel)
            db.session.commit()
            flash('Artikel succesvol toegevoegd', category='modal')
            return redirect(url_for('views.artikelbeheer'))
        except Exception as e:
            #kijkt na als de admin fout info toevoegt
             flash('Fout van het toevoegen van artikel {e}' ,category='modalerror')
             return redirect(url_for('views.additem'))

    artikels = Artikel.query.all()
    users = current_user 
    return render_template('additem.html', artikels = artikels, user=users)



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
        flash('Artikel verlengd.', category='modal')
        msg = Message('Artikel verlengd', recipients=[uitlening.user.email, "louisingelbrecht@gmail.com"])
        msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} verlengd.\n\nDe nieuwe einddatum is: {uitlening.end_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
        mail.send(msg)
        return redirect('/userartikels')
    
    while (uitlening.verlengd == True):
        flash('Artikel kan niet verlengd worden.', category='modalerror')
        return redirect('/userartikels')
    

#Route om een reservatie te annuleren
@views.route('/verwijder/<int:id>', methods=['GET', 'PUT'])
def verwijder(id):
    uitlening = Uitlening.query.get_or_404(id)

    try:
        msg = Message('Reservatie geannuleerd', recipients=[uitlening.user.email, "louisingelbrecht@gmail.com"])
        msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft de reservatie van het artikel {uitlening.artikel.title} geannuleerd.\n\nMet vriendelijke groeten,\nDe uitleendienst'
        mail.send(msg)
        uitlening.artikel.user_id = None
        db.session.delete(uitlening)
        db.session.commit()
        flash('Reservatie geannuleerd.', category='modal')
        
        return redirect('/userartikels')
    except:
        flash('Reservatie verwijderen mislukt.', category='modalerror')
        return redirect('/userartikels')


#Route naar gebruikersprofiel
@views.route("/gebruikersprofiel", methods=['GET', 'POST'])
@login_required
def gebruikersprofiel():
    user = current_user
    if request.method == "POST":
        phone_number = request.form.get('phoneInput')
        file = request.files.get('profile_picture')
        
        if phone_number:
            if check_input(phone_number) == False:
                return render_template('gebruikersprofiel.html', user= user)
            user.phone_number = phone_number
            db.session.commit()
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('website/static/profiles', filename)  
            file.save(os.path.join('website/static/profiles', filename))
            user.profile_picture = filename
            db.session.commit()
            flash('Profielfoto succesvol gewijzigd.', category='modal')
            return redirect(url_for('views.gebruikersprofiel'))

    return render_template('gebruikersprofiel.html', user= user)    
 

     
