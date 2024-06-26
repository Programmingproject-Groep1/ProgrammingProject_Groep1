from flask import Blueprint, app, render_template, request, redirect, flash, send_from_directory, jsonify, url_for, abort, request, session
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
from sqlalchemy import func

views = Blueprint('views', __name__)

# Routes

#Zorgt ervoor dat de gereserveerde datums van de artikels getoond kunnen worden

@views.route('/reserved_dates')
@login_required #je kan enkel op de pagina als je ingelogd bent
def reserved_dates():
    uitleningen = Uitlening.query.filter(Uitlening.user_id == current_user.id).all() #Alle uitleningen ophalen
    reserved_dates_dict = {}
    for uitlening in uitleningen:
        if uitlening.artikel_id not in reserved_dates_dict:
            reserved_dates_dict[uitlening.artikel_id] = []
        date_range = pd.date_range(start=uitlening.start_date, end=uitlening.end_date)
        for date in date_range:
            reserved_dates_dict[uitlening.artikel_id].append(date.strftime('%Y-%m-%d'))  # format date as string

    return jsonify(reserved_dates_dict) # return dictionary als JSON object

#Zorgt dat artikel getoond kan worden bij invoeren van id in admin dashboard
@views.route('/get-artikel')
@login_required
def get_artikel():
    if current_user.type_id == 1:   #Enkel admins kunnen op de pagina als er usertype 1 staat
        id = request.args.get('id')
        artikel = Artikel.query.get(id)
        if Artikel is None:
            return jsonify(modalerror='Artikel bestaat niet'), 404
        
        afbeelding_url = url_for('static', filename=f'images/{artikel.afbeelding}')
        return jsonify(title = artikel.title, afbeelding = afbeelding_url)
    else:
        return abort(403)

#Zorgt dat user getoond kan worden bij invoeren van id in admin dashboard
@views.route('/get-user')
@login_required
def get_user():
    if current_user.type_id == 1:    
        id = request.args.get('id')
        user = User.query.get(id)
        if user is None:
            return jsonify(modalerror='User bestaat niet'), 404
    
        
        return jsonify(user = (user.first_name + " " + user.last_name))
    else:
        return abort(403)

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
@login_required
def infopagina():
    user = current_user #User doorgeven voor navbar
    return render_template('infopagina.html', user= user)

#Route naar historiek
@views.route("/historiek", methods=['GET', 'POST'])
@login_required
def historiek():
    user = current_user
    uitleningen = Uitlening.query.all()  # Alle uitleningen ophalen
    if request.method == 'POST':
        if request.form.get('form_name') == 'search': # Als er gezocht wordt
            search = request.form.get('search')
            if check_input(search) == False: # Checken op verboden tekens
                return redirect('/historiek')
            else:
                search = f'%{search}%'
                uitleningen = Uitlening.query.outerjoin(User, Uitlening.user_id == User.id).outerjoin(Artikel, Uitlening.artikel_id == Artikel.id).filter(
                    or_(
                        Uitlening.artikel_id.ilike(search), #ilike zodat zoekopdracht niet hoofdlettergevoelig is
                        User.id.ilike(search),
                        Artikel.title.ilike(search),
                        User.first_name.ilike(search),
                        User.last_name.ilike(search),     
                    )
                ).all()                    
    return render_template('historiek.html', user=user, uitleningen=uitleningen)

    


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
                if not artikelid or not userid: #Als er geen artikel of user-ID ingevoerd is
                    flash('Geen artikel of user-ID ingevoerd.', category='modalerror')
                    return redirect('/')
                uitlening = Uitlening.query.filter(Uitlening.artikel_id == artikelid, Uitlening.return_date == None).first()
                if uitlening and uitlening.actief: #Als het artikel al opgehaald is
                    flash('Artikel is al opgehaald.', category='modalerror')
                elif uitlening and uitlening.user_id == int(userid): #Als alle gegevens kloppen
                    uitlening.actief = True
                    db.session.commit()
                    flash('Artikel opgehaald', category='modal')
                    msg = Message('Artikel opgehaald', recipients=[uitlening.user.email])
                    msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} opgehaald.\n\nDeze reservering loopt van: {uitlening.start_date} tot {uitlening.end_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                    mail.send(msg)
                    redirect('/')
                elif uitlening and uitlening.user_id != int(userid): #Als de user-ID niet klopt
                    flash('User-ID behoort niet tot deze uitlening.', category='modalerror')
                elif not uitlening: #Als het artikel niet gereserveerd is
                    gebruiker = User.query.get(userid)
                    if not gebruiker: #Checken of de user bestaat
                        flash('User-ID niet gevonden.', category='modalerror')
                        return redirect('/')
                    uitlening = Uitlening(user_id = userid, artikel_id = artikelid, start_date = datumbeginweek, end_date = datumeindweek)
                    uitlening.actief = True
                    artikel = Artikel.query.get(artikelid)
                    artikel.user_id = userid
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
                gebruiker = User.query.get(userid)
                if not gebruiker: #Checken of de user bestaat
                    flash('User-ID niet gevonden.', category='modalerror')
                    return redirect('/')
                uitlening = Uitlening.query.filter(Uitlening.artikel_id == artikelid, Uitlening.actief).first()
                schade = request.form.get('schade')
                artikel = Artikel.query.get(artikelid)
                if uitlening and uitlening.user_id == int(userid): #Als alle gegevens kloppen
                    #Indien er schade is: Beschrijving van de schade en foto van de schade worden toegevoegd
                    if schade == 'ja':
                        uitlening.schade_beschrijving = request.form.get('schadeBeschrijving')
                        uitlening.actief = False
                        gebruik = request.form.get('gebruik')
                        file = request.files['file'] if 'file' in request.files else None
                        uitlening.return_date = date.today()
                        artikel.user_id = None
                        if gebruik == 'nee': #Als het artikel niet meer gebruikt kan worden
                            artikel.actief = 0
                        else: #Als het artikel nog gebruikt kan worden
                            artikel.actief = 1
                        if file and allowed_file(file.filename): #Als er een foto van de schade is en het bestand toegestaan is
                            filename = secure_filename(file.filename)
                            file.save(os.path.join('website/static/schade', filename))
                            uitlening.schade_foto = filename
                        db.session.commit()
                        msg = Message('Artikel ingeleverd', recipients=[uitlening.user.email])
                        msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} ingeleverd op: {uitlening.return_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                        mail.send(msg)
                        flash('Schade gemeld en artikel ingeleverd.', category='modal')   
                    else: #Als er geen schade is
                        uitlening.actief = False
                        uitlening.return_date = date.today()
                        msg = Message('Artikel ingeleverd', recipients=[uitlening.user.email])
                        msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} ingeleverd op: {uitlening.return_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                        mail.send(msg)
                        artikel.user_id = None
                        artikel.actief = 1
                        db.session.commit()
                        flash('Artikel ingeleverd', category='modal')
                elif uitlening and uitlening.user_id != int(userid): #Als de user-ID niet klopt
                    flash('User-ID behoort niet tot deze uitlening.', category='modalerror')
                else: #Als het artikel niet uitgeleend is
                    flash('Artikel niet gevonden bij uitleningen.', category='modalerror')
            #Als de user op de knop klikt om de week te resetten
            elif request.form.get('form_name') == 'reset_week':
                return redirect('/')
        elif request.method == 'GET':
            session['weken'] = 0 #Zorgen dat pagina altijd op huidige week staat als pagina geladen wordt
        datumbeginweek += timedelta(days=7 * session.get('weken', 0)) 
        datumeindweek += timedelta(days=7 * session.get('weken', 0))
        if datumbeginweek == (date.today() - timedelta(days=(date.today().weekday() + 7) % 7)):
            huidigeWeek = True
        #Artikels die opgehaald moeten worden
        artikelsophaal = Uitlening.query.filter(Uitlening.start_date >= datumbeginweek , ~Uitlening.actief, Uitlening.return_date == None, Uitlening.start_date <= datumeindweek).all() 
        #Artikels die teruggebracht moeten worden
        artikelsterug = Uitlening.query.filter(Uitlening.end_date <= datumeindweek , Uitlening.actief, Uitlening.return_date == None, Uitlening.end_date >= datumbeginweek).all() 
        #Artikels die te laat zijn
        artikelsOvertijd = Uitlening.query.filter(Uitlening.end_date < date.today(), Uitlening.actief, Uitlening.return_date == None).all()
        #Rendert de template voor de admin homepagina    
        return render_template("homeadmin.html", user=current_user, artikelsophaal=artikelsophaal or [], artikelsterug = artikelsterug or [], datumbeginweek = datumbeginweek, datumeindweek= datumeindweek, artikelsOvertijd = artikelsOvertijd or [], huidigeWeek = huidigeWeek)
            
    #Als de user een student of docent is
    elif current_user.type_id == 3 or current_user.type_id == 2:
        is_multiple_dict = {} #Artikels met meerdere exemplaren bijhouden
        unavailable_article_ids = [] #Artikels die niet beschikbaar zijn bijhouden
        selected_categories = [] #Geselecteerde categorieën bijhouden
        selected_merk = [] #Geselecteerde merken bijhouden
        selected_type = [] #Geselecteerde type bijhouden
        sortItems = None
        begindatum = None
        einddatum = None
        artikels = Artikel.query.filter_by(actief=True).all() #Alle zichtbare artikels ophalen
        if request.method == 'POST':
            formNaam = request.form.get('form_name')
            # Standaardquery
            subquery = db.session.query(func.max(Artikel.id)).group_by(Artikel.title).subquery()
            query = db.session.query(Artikel).filter(Artikel.id.in_(subquery), Artikel.actief == True)

            if formNaam == 'sorteer': #Als de user wil sorteren
                sortItems = request.form.get('AZ')
                selected_categories = request.form.getlist('category')
                selected_merk = request.form.getlist('merk')
                selected_type = request.form.getlist('Type_product')
                datums = request.form.get('datums').split(' to ')
                if len(datums) == 2: #Als er een start- en einddatum ingevoerd zijn
                    begindatum = datetime.strptime(datums[0], '%Y-%m-%d')
                    einddatum = datetime.strptime(datums[1], '%Y-%m-%d')

                # Category filter
                if selected_categories: #Als categorieën geselecteerd zijn
                    query = query.filter(Artikel.category.in_(selected_categories))

                # Merk filter
                if selected_merk: #Als merken geselecteerd zijn
                    query = query.filter(Artikel.merk.in_(selected_merk))

                # Type product filter
                if selected_type: #Als type producten geselecteerd zijn
                    query = query.filter(Artikel.type_product.in_(selected_type))

                # Date range filter
                if begindatum and einddatum: #Als er een start- en einddatum ingevoerd zijn
                    conflict_subquery = db.session.query(Uitlening.artikel_id).filter(
                        or_(
                            and_(Uitlening.start_date <= einddatum, Uitlening.end_date >= begindatum),
                            and_(Uitlening.start_date.is_(None), Uitlening.end_date.is_(None))
                        )
                    ).subquery()
                    unavailable_article_ids = [result[0] for result in db.session.query(conflict_subquery).all()]

                # Sorteren
                if sortItems == 'AZ': #Als de user op AZ sorteert
                    query = query.order_by(Artikel.title)
                elif sortItems == 'ZA': #Als de user op ZA sorteert
                    query = query.order_by(Artikel.title.desc())

                artikels = query.all()

            elif formNaam == 'search': #Als de user wil zoeken
                search = request.form.get('search')
                if check_input(search) == False: #Checken op verboden tekens
                    flash('Ongeldige invoer: verboden tekens', category='modalmodalerror')
                    return redirect('/')
                else:
                    artikels = db.session.query(Artikel).filter(
                        Artikel.id.in_(subquery),
                        Artikel.title.like(f'%{search}%'),
                        Artikel.actief == True
                    ).all()

            elif formNaam == 'reserveer': #Als artikel gereserveerd word
                if current_user.blacklisted: #Als de user geband is
                    flash('Je bent geband en kan geen artikelen reserveren.', category='modalmodalerror')
                    return redirect('/')
                
                datums = request.form.get('datepicker').split(' to ') #Start- en einddatum ophalen
                artikelid = request.form.get('artikel_id')
                artikel = Artikel.query.get_or_404(artikelid)
                meerdere_exemplaren = Artikel.query.filter_by(title=artikel.title).all() #Alle exemplaren van het artikel ophalen
                if len(datums) != 2 or not datums[0] or not datums[1]: #Als er geen start- of einddatum ingevoerd is
                    flash('Gelieve een start- en einddatum te selecteren.', category='modalerror')
                    return redirect('/')
                
                startDatum = datetime.strptime(datums[0], '%Y-%m-%d') #Start- en einddatum omzetten naar datetime
                eindDatum = datetime.strptime(datums[1], '%Y-%m-%d')

                if startDatum.weekday() != 0 or eindDatum.weekday() != 4: #Als de start- of einddatum geen maandag of vrijdag is
                    flash('Afhalen is alleen mogelijk op maandag en terugbrengen op vrijdag', category='modalerror')
                    return redirect('/')
                elif current_user.type_id == 2 and (eindDatum - startDatum).days > 5: #Als de user een student is en de reservatie langer dan 5 dagen is
                    flash('Reservatie voor studenten kan maximum 5 dagen lang zijn', category='modalerror')
                    return redirect('/')
                elif current_user.type_id == 2 and (startDatum - datetime.today()).days > 14: #Als de user een student is en de reservatie meer dan 14 dagen op voorhand is
                    flash('Studenten kunnen pas 14 dagen op voorhand reserveren', category='modalerror')
                    return redirect('/')

                vrij_artikel_gevonden = False
                for artikel in meerdere_exemplaren: #Alle exemplaren van het artikel overlopen, kijken of er een vrij is
                    uitlening = Uitlening.query.filter(Uitlening.artikel_id == artikel.id,
                                                    and_(Uitlening.start_date < eindDatum, Uitlening.end_date > startDatum)).first()

                    if uitlening is None: #Als er geen uitlening is voor 1 van de exemplaren
                        new_uitlening = Uitlening(user_id=current_user.id, artikel_id=artikel.id, start_date=startDatum, end_date=eindDatum)
                        db.session.add(new_uitlening)
                        db.session.commit()
                        flash('Reservatie gelukt.', category='modal')
                        msg = Message('Reservering bevestigd', recipients=[new_uitlening.user.email])
                        msg.body = f'Beste {new_uitlening.user.first_name},\n\nHierbij bevestigen we de reservering van het artikel: {new_uitlening.artikel.title}\n\nDe reservering loopt van {new_uitlening.start_date} tot {new_uitlening.end_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                        mail.send(msg)
                        vrij_artikel_gevonden = True
                        break

                if not vrij_artikel_gevonden: #Als er geen vrij artikel gevonden is
                    flash('Artikel is al gereserveerd in deze periode.', category='modalerror')
                    return redirect('/')

                # Artikels en multiple_dict updaten na reservatie
                subquery = db.session.query(func.max(Artikel.id)).group_by(Artikel.title).subquery()
                artikels = db.session.query(Artikel).filter(Artikel.id.in_(subquery), Artikel.actief == True).all()
                is_multiple_dict = {artikel.id: Artikel.query.filter_by(title=artikel.title).count() > 1 for artikel in artikels}

                return render_template("home.html", user=current_user, artikels=artikels, is_multiple_dict=is_multiple_dict, unavailable_article_ids=unavailable_article_ids)
                
        else:
            subquery = db.session.query(func.max(Artikel.id)).group_by(Artikel.title).subquery()
            artikels = db.session.query(Artikel).filter(Artikel.id.in_(subquery), Artikel.actief == True).all()

        
        is_multiple_dict = {artikel.id: Artikel.query.filter_by(title=artikel.title).count() > 1 for artikel in artikels}

        return render_template("home.html", 
                            user=current_user, 
                            artikels=artikels, 
                            is_multiple_dict=is_multiple_dict, 
                            unavailable_article_ids=unavailable_article_ids,
                            selected_categories=selected_categories,
                            selected_merk=selected_merk,
                            selected_type=selected_type,
                            sortItems=sortItems,
                            begindatum=begindatum,
                            einddatum=einddatum)

#Route voor admin blacklist
@views.route('/adminblacklist', methods=['GET', 'POST'])
@login_required
def admin_blacklist():
    if current_user.type_id == 1:
        # kijken of de gebruiker een admin is
        if current_user.type_id == 1:
            if request.method == 'POST':
                # Als gebruiker wordt geband
                if request.form.get('form_name') == 'ban':
                    user_id = request.form.get('userid')
                    reden_blacklist = request.form.get('reden_blacklist')
                    user = User.query.get(user_id)
                    if user: # Als de gebruiker bestaat
                        user.blacklisted = True
                        user.reden_blacklist = reden_blacklist
                        # laat de geruiker gebanned worden voor 3 maanden
                        user.blacklist_end_date = datetime.now() + timedelta(days=90)
                        #melding meegeven
                        db.session.commit()
                        flash('Gebruiker verbannen voor 3 maanden.', category='modal')
                    else: # Als de gebruiker niet bestaat
                        flash('Gebruiker niet gevonden.', category='modalerror')
                # Als de gebruiker wordt geunbaned
                elif request.form.get('form_name') == 'unban': #Om user te unbannen
                    user_id = request.form.get('userid')
                    user = User.query.get(user_id)
                    if user: # Als de gebruiker bestaat de user unbannen en alle waarden terugzetten
                        user.blacklisted = False
                        user.blacklist_end_date = None
                        user.warning = 0
                        db.session.commit()
                        flash('Gebruiker is niet langer verbannen.', category='modal')
                    else: # Als de gebruiker niet bestaat
                        flash('Gebruiker niet gevonden.', category='modalerror')

                # Als de ADMIN de gebruiker_type wil wijzigen
                elif request.form.get('form_name') == 'change_type':
                    user_id = request.form.get('user_id')
                    new_type_id = request.form.get('type_gebruiker')  # verander 'type_id' naar 'type_gebruiker'
                    user = User.query.get(user_id)
                    if user: # Als de gebruiker bestaat
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
            
            search_term = request.form.get('search') # Zoeken op voornaam of achternaam
            if search_term:
                query = query.filter(or_(User.first_name.ilike(f'%{search_term}%'), User.last_name.ilike(f'%{search_term}%')))
                
            users = query.all()
            # Rendert de template voor de blacklistpagina
    
            return render_template("adminblacklist.html", user=current_user, users=users, filter_option=filter_option, weergaven=weergaven)
    
    else:
        abort(403)        
        
        
#Zorgt ervoor dat images geladen kunnen worden
@views.route('images/<path:filename>')
@login_required
def get_image(filename):
    return send_from_directory('images', filename)

#Route naar artikelbeheer
@views.route('/adminartikels', methods=['GET', 'POST'])
@login_required
def artikelbeheer():
    if current_user.type_id == 1: #Enkel voor admins
        artikels = Artikel.query.all()
        
        user = current_user
        if request.method == 'POST':
            formNaam = request.form.get('form_name')
            if formNaam == 'sorteer': #Als de user wil sorteren/filteren
                sortItems = request.form.get('AZ')
                selected_categories = request.form.getlist('category')
                selected_merk = request.form.getlist('merk')
                selected_type = request.form.getlist('Type_product')

                # de query van uitleen en artikel joinen
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

                                    
            
            elif formNaam == 'search': #Als de user wil zoeken
                search = request.form.get('search')
                if check_input(search) == False: #Checken op verboden tekens
                    flash('Ongeldige invoer: verboden tekens', category='modalerror')
                    return redirect('/adminartikels')
                else:
                    artikels = Artikel.query.filter(Artikel.title.like(f'%{search}%')).all()
                    grouped_artikels = {k: list(v) for k, v in groupby(artikels, key=attrgetter('title'))}
                    return render_template('adminartikels.html', artikels=artikels,
                                            user=user, grouped_artikels=grouped_artikels)
            
        # Als het formulier wordt ingediend
        if request.method == 'POST': 
            if 'save' in request.form: #Als de user wijzigingen wil opslaan
                artikelId = request.form.get('id')
                artikel = Artikel.query.get(artikelId)
                if artikel: #Als het artikel gevonden is
                    file = request.files["afbeelding_" + str(artikel.id)]
                    title = request.form.get("titleInput")
                    merk = request.form.get("merkInput")
                    category = request.form.get("categoryInput")
                    description = request.form.get("descriptionInput")
                    

                    if file and allowed_file(file.filename): #Als er een afbeelding is en het bestand toegestaan is
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
                    elif not file: #Als er geen afbeelding is
                        artikel.title = title
                        artikel.merk = merk
                        artikel.category = category
                        artikel.beschrijving = description
                        artikel.actief = not artikel.actief
                        db.session.commit()
                        flash('Artikel succesvol gewijzigd', category='modal')
                    else: #Als het bestand niet toegestaan is
                        flash('Ongeldige afbeelding', category='modalerror')
                else: #Als het artikel niet gevonden is
                    flash('Artikel niet gevonden', category='modalerror')
                return redirect(url_for('views.artikelbeheer'))
            elif 'delete' in request.form: #Als de user een artikel wil verwijderen
                artikelId = request.form.get('id')
                artikel = Artikel.query.get(artikelId)
                if artikel: #Als het artikel gevonden is
                    db.session.delete(artikel)
                    db.session.commit()
                    flash('Artikel succesvol verwijderd', category='modal')
                else: #Als het artikel niet gevonden is
                    flash('Artikel niet gevonden', category='modalerror')
                return redirect(url_for('views.artikelbeheer'))

        return render_template('adminartikels.html', artikels=artikels, user=user,)
    else:
        abort(403)        

#route naar additem en toevoegen van product
@views.route('/additem', methods=['GET', 'POST'])
@login_required
def additem():
    if current_user.type_id == 1:
        if request.method == 'POST': #Als de user een artikel wil toevoegen
            #data halen uit van de admin
            merk = request.form['merk']
            title = request.form['title']
            nummer = request.form['nummer']
            category = request.form['category']
            type_product = request.form['type']
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
                type_product = type_product,
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
                type_product = type_product,
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
    else:
        abort(403)
  


#Pagina waar user zijn reserveringen kan bekijken
@views.route('/userartikels' , methods=['GET', 'POST'])
@login_required
def reservaties():
    uitleningen_actief = Uitlening.query.filter(Uitlening.user_id == current_user.id, Uitlening.actief).all()
    uitleningen = Uitlening.query.filter(Uitlening.user_id == current_user.id, Uitlening.actief == False).all()
    uitlening_teruggebracht = Uitlening.query.filter(Uitlening.user_id == current_user.id, Uitlening.actief == False, Uitlening.return_date != None).all()
    artikels = Artikel.query.filter(Artikel.id.in_([uitlening.artikel_id for uitlening in uitleningen])).all()
    if request.method == "POST":
        form_name = request.form.get('form_name')
        uitlening_id = request.form.get('uitlening_id')
        uitlening = Uitlening.query.get(uitlening_id)
        if form_name == 'verleng': #Als de user een artikel wil verlengen
            verlengartikel = Uitlening.query.filter( Uitlening.artikel_id == uitlening.artikel_id, Uitlening.start_date <= (uitlening.end_date + timedelta(days=7)), Uitlening.start_date > uitlening.end_date).first()
            if verlengartikel: #Als het artikel al gereserveerd is voor de volgende week
                flash('Artikel kan niet verlengd worden.', category='modalerror')
                return redirect('/userartikels')
            
            if (uitlening.verlengd == False): #Als het artikel nog niet verlengd is
                uitlening.end_date += timedelta(days=7)
                uitlening.verlengd = True
                db.session.commit()
                flash('Artikel verlengd.', category='modal')
                msg = Message('Artikel verlengd', recipients=[uitlening.user.email])
                msg.body = f'Beste {uitlening.user.first_name},\n\nU heeft het artikel {uitlening.artikel.title} verlengd.\n\nDe nieuwe einddatum is: {uitlening.end_date}\n\nMet vriendelijke groeten,\nDe uitleendienst'
                mail.send(msg)
                return redirect('/userartikels')
            else: #Als het artikel al verlengd is
                flash('Artikel kan niet verlengd worden.', category='modalerror')
                return redirect('/userartikels')
        elif form_name == "annuleer": #Als de user een reservering wil annuleren
            try:
                msg = Message('Reservatie geannuleerd', recipients=[uitlening.user.email])
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
    return render_template('userartikels.html', uitleningen=uitleningen, user=current_user, artikels=artikels, uitleningen_actief=uitleningen_actief, uitlening_teruggebracht=uitlening_teruggebracht)



#Route naar gebruikersprofiel
@views.route("/gebruikersprofiel", methods=['GET', 'POST'])
@login_required
def gebruikersprofiel():
    user = current_user 
    if request.method == "POST":
        phone_number = request.form.get('phone_number')
        file = request.files.get('profile_picture')
        
        
        if phone_number: #Als er een telefoonnummer ingevoerd is
            if not check_input(phone_number):
                print("Invalid phone number")
                return render_template('gebruikersprofiel.html', user= user)
            current_user.phone_number = phone_number
           

        if file and allowed_file(file.filename): #Als er een profielfoto geüpload wordt
            filename = secure_filename(file.filename)
            file.save(os.path.join('website/static/profiles', filename))
            current_user.profile_picture = filename
    
        db.session.commit()
    return render_template('gebruikersprofiel.html', user= user)
 


     
