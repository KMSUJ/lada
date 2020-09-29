import datetime
import logging

import flask_featureflags as feature
from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, or_
from werkzeug.urls import url_parse

import lada.fellow
from lada import db
from lada.fellow import bp
from lada.fellow.board import board_required
from lada.constants import *
from lada.fellow.email import send_password_reset_email
from lada.fellow.forms import LoginForm, RegisterForm, EditForm, ViewForm, PanelForm, PasswordResetRequestForm, \
  PasswordResetForm
from lada.models import Fellow

log = logging.getLogger(__name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('base.index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        log.debug(f'Login attempt for: {email}')
        fellow = Fellow.query.filter_by(email=email).first()
        if fellow is None or not fellow.check_password(form.password.data):
            flash('Invalid username or password')
            log.warning(f'Invalid username or password for {form.email.data}')
            return redirect(url_for('fellow.login'))
        login_user(fellow, remember=form.remember_me.data)
        log.info(f'Logged as {fellow}')
        flash('Logged in.')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('base.index')
            return redirect(next_page)
    return render_template('fellow/login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('base.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('base.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        lada.fellow.register(
            email=form.email.data,
            password=form.password.data,
            name=form.name.data,
            surname=form.surname.data,
            studentid=form.studentid.data,
            newsletter=32
        )
        flash('Registration successful.')
        return redirect(url_for('fellow.login'))
    return render_template('fellow/register.html', form=form)


@bp.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        fellow = Fellow.query.filter_by(email=form.email.data).first()
        if fellow:
            send_password_reset_email(fellow)
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('fellow.login'))
    return render_template('fellow/password_reset_request.html', form=form)


@bp.route('/password_reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    fellow = Fellow.verify_password_reset_token(token)
    if not fellow:
        return redirect(url_for('base.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        fellow.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('password_reset.html', form=form)


def activate(fellow, value=True):
    if value and not fellow.check_board('fellow'):
        fellow.joined = datetime.datetime.utcnow()
        fellow.set_board('fellow', True)
    fellow.set_board('active', value)
    return


@bp.route('/view/<id>', methods=['GET', 'POST'])
@login_required
def view(id):
    form = ViewForm()
    fellow = Fellow.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        if form.activate.data:
            activate(fellow)
        else:
            activate(fellow, False)
        db.session.commit()
    return render_template('fellow/view.html', fellow=fellow, form=form)


# delete this later
@bp.route('/cleardb')
def cleardb():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        log.info(f'Clear table {table}')
        db.session.execute(table.delete())
    db.session.commit()
    flash(f'Database Clear')
    return redirect(url_for('fellow.register'))


@bp.route('/seeddb')
@feature.is_active_feature('demo')
def seeddb():
    log.info('Seeding fellow db')
    admin = lada.fellow.register(
        email='admin@kms.uj.edu.pl',
        password='admin',
        name='Jedyny Słuszny',
        surname='Admin',
        studentid='62830',
    )

    admin.set_board('active', True)
    admin.set_board('fellow', True)
    admin.set_board('board', True)
    admin.set_board(POSITION_BOSS, True)

    names = {'Adrian', 'Zofia', 'Baltazar', 'Weronika', 'Cezary', 'Urszula', 'Dominik', 'Telimena', 'Euzebiusz',
             'Sabrina', 'Filemon', 'Roksana', 'Grzegorz', 'Patrycja', 'Henryk', 'Ofelia', 'Iwan', 'Nina', 'Jeremiasz',
             'Monika', 'Klaus', 'Laura'}
    surs = {'Albinos', 'Bez', 'Chryzantema', 'Dalia', 'Ekler', 'Fiat', 'Gbur', 'Hałas', 'Irys', 'Jabłoń', 'Kwiat',
            'Lewak', 'Mikrus', 'Nektar', 'Okular', 'Prokocim', 'Rabarbar', 'Sykomora', 'Trzmiel', 'Ul', 'Wrotek',
            'Zlew'}
    for i, p in enumerate(zip(names, surs)):
        fellow = lada.fellow.register(
            email=f'{p[1].lower()}.{p[0].lower()}@kms.uj.edu.pl',
            password=f'{p[0]}{i}{p[1]}',
            name=p[0],
            surname=p[1],
            studentid=i,
        )

        fellow.set_board('active', True)
        fellow.set_board('fellow', True)
    flash('Database Seeded')
    return redirect(url_for('base.index'))


# end delete

@bp.route('/panel', methods=['GET', 'POST'])
@board_required([POSITION_TREASURE, ])
@login_required
def panel():
    form = PanelForm()
    fellows = Fellow.query.order_by(desc(Fellow.id)).limit(12).all()
    if form.validate_on_submit():
        fellows = Fellow.query.order_by(desc(Fellow.id)).filter(or_(
            Fellow.name.like(f'%{form.search.data}%'),
            Fellow.surname.like(f'%{form.search.data}%'),
            Fellow.studentid.like(f'%{form.search.data}%')
        )).limit(12).all()
        return render_template('fellow/panel.html', fellows=fellows, form=form)
    return render_template('fellow/panel.html', fellows=fellows, form=form)


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(current_user.studentid)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.studentid = form.studentid.data
        current_user.phone = form.phone.data
        current_user.shirt = form.shirt.data
        current_user.set_newsletter('wycinek', form.wycinek.data)
        current_user.set_newsletter('cnfrnce', form.cnfrnce.data)
        current_user.set_newsletter('anteomnia', form.anteomnia.data)
        current_user.set_newsletter('fotki', form.fotki.data)
        current_user.set_newsletter('fszysko', form.fszysko.data)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('fellow.edit'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.studentid.data = current_user.studentid
        form.phone.data = current_user.phone
        form.shirt.data = current_user.shirt
        form.wycinek.data = current_user.check_newsletter('wycinek')
        form.cnfrnce.data = current_user.check_newsletter('cnfrnce')
        form.anteomnia.data = current_user.check_newsletter('anteomnia')
        form.fotki.data = current_user.check_newsletter('fotki')
        form.fszysko.data = current_user.check_newsletter('fszysko')
    return render_template('fellow/edit.html', form=form)
