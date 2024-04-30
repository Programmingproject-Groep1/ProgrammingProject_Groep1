from flask import Blueprint, render_template, request, redirect, flash, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, Artikel, Uitlening
from datetime import datetime


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'PUT', 'POST'])
@login_required
def home():
    if (request.method == 'PUT'):
        sortItems = request.form.get('AZ')
        category = request.form.get('category')
        if sortItems == 'az':
            artikels = Artikel.query.order_by(Artikel.title).all()
            return render_template("home.html", user=current_user, artikels = artikels)
        elif sortItems == 'za':
            artikels = Artikel.query.order_by(Artikel.title.desc()).all()
            return render_template("home.html", user=current_user, artikels = artikels)
        if category == 'all':
            artikels = Artikel.query.all()
            return render_template("home.html", user=current_user, artikels = artikels)
        elif category == 'audio':
            artikels = Artikel.query.filter_by(category = 'Audio').all()
            return render_template("home.html", user=current_user, artikels = artikels)
        elif category == 'video':
            artikels = Artikel.query.filter_by(category = 'Video').all()
            return render_template("home.html", user=current_user, artikels = artikels)
        elif category == 'varia':
            artikels = Artikel.query.filter_by(category = 'Varia').all()
            return render_template("home.html", user=current_user, artikels = artikels)
        elif category == 'belichting':
            artikels = Artikel.query.filter_by(category = 'Belichting').all()
            return render_template("home.html", user=current_user, artikels = artikels)
        elif category == 'xr':
            artikels = Artikel.query.filter_by(category = 'XR').all()
            return render_template("home.html", user=current_user, artikels = artikels)
        
    if (request.method == 'POST'): 
        datums = request.form.get('datepicker').split(' to ')
        artikelid = request.form.get('artikel_id')
        
        try:
            startDatum = datetime.strptime(datums[0], '%Y-%m-%d')
            eindDatum = datetime.strptime(datums[1], '%Y-%m-%d')
            if startDatum.weekday() >= 5 or eindDatum.weekday() >= 5:
                raise ValueError('Reservatie is niet toegestaan op zaterdag of zondag')
            if current_user.type_id == 2 and (startDatum.weekday() == 4 or eindDatum.weekday() == 4):
                raise ValueError('Reservatie is niet toegestaan voor studenten')
            elif current_user.type_id == 2 and (eindDatum - startDatum).days > 7:
                raise ValueError('Reservatie is niet toegestaan voor studenten langer dan 7 dagen')
            new_uitlening = Uitlening(user_id = current_user.id, artikel_id = artikelid, start_date = startDatum, end_date = eindDatum)
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
        
        
        
    
    artikels = Artikel.query.all()
    return render_template("home.html", user=current_user, artikels = artikels)

@views.route('images/<path:filename>')
def get_image(filename):
    return send_from_directory('images', filename)




@views.route('/userartikels')
@login_required
def reservaties():
    uitleningen = Uitlening.query.filter_by(user_id = current_user.id).all()
    artikels = Artikel.query.all()
    return render_template('userartikels.html', uitleningen = uitleningen, user=current_user, artikels = artikels)


@views.route('/verwijder/<int:id>', methods=['GET', 'PUT'])
def verwijder(id):
    uitlening = Uitlening.query.get_or_404(id)

    try:
        db.session.delete(uitlening)
        db.session.commit()
        return redirect('/userartikels')
    except:
        flash('Reservatie verwijderen mislukt.', category='error')
        return redirect('/userartikels')
