import datetime
import logging

import click
import flask_featureflags as feature
from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, func, or_
from werkzeug.urls import url_parse

import lada.fellow
from lada import db
from lada.models import Fellow, news_flags, board_flags
from lada.constants import *
from lada.base.board import board_required
from lada.fellow import bp
from lada.fellow.email import send_password_reset_email, send_verification_email, send_import_email
from lada.fellow.forms import LoginForm, RegisterForm, EditForm, ViewForm, PanelForm, PasswordResetRequestForm, \
    PasswordResetForm
from lada.dike.maintenance import compute_fellows_checksum

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
        fellow = lada.fellow.register(
            email=form.email.data,
            password=form.password.data,
            name=form.name.data,
            surname=form.surname.data,
            studentid=form.studentid.data,
            newsletter=news_flags[NEWS_ALL]
        )
        log.info(f"New fellow registered: {fellow}")
        if feature.is_active(FEATURE_EMAIL_VERIFICATION):
            send_verification_email(fellow)
            flash('Registration successful. Please check your e-mail, including SPAM, for verification e-mail.')
        else:
            fellow.set_verified(True)
            flash('Registration successful.')
        return redirect(url_for('fellow.login'))
    return render_template('fellow/register.html', form=form)


@bp.route('/send_verification_token', methods=['GET'])
@feature.is_active_feature(FEATURE_EMAIL_VERIFICATION)
def send_verification_token():
    send_verification_email(current_user)
    flash('Verification token sent. Please check your e-mail, including SPAM, for verification e-mail.')
    return redirect(url_for('fellow.login'))


@bp.route('/verify/<token>', methods=['GET'])
def verify(token):
    fellow = Fellow.decode_verification_token(token)
    if fellow is None:
        flash('Invalid verification token.')
        return redirect(url_for('base.index'))

    fellow.set_verified(True)
    flash('Your account has been verified')
    return redirect(url_for('fellow.login'))


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
    fellow = Fellow.decode_reset_password_token(token)
    if not fellow:
        return redirect(url_for('base.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        fellow.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('fellow.login'))
    return render_template('fellow/password_reset.html', form=form)


def activate(fellow, value=True):
    if value:
        fellow.set_verified(True)
        fellow.set_board(FELLOW_FELLOW, True)
        fellow.activate()
    else:
        fellow.deactivate()


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


@bp.route('/panel', methods=['GET'])
@board_required([POSITION_TREASURE, ])
@login_required
def panel():
    form = PanelForm(meta={'csrf': False}, formdata=request.args)
    if form.validate():
        fellows = Fellow.query

        if form.search.data:
            fellows = fellows.filter(or_(
                Fellow.name.like(f'%{form.search.data}%'),
                Fellow.surname.like(f'%{form.search.data}%'),
                Fellow.studentid.like(f'%{form.search.data}%')
            ))

        if form.active.data:
            fellows = fellows.filter(
                Fellow.board.op('&')(board_flags[FELLOW_ACTIVE])
            )

        fellows = fellows.order_by(Fellow.surname.asc(), Fellow.name.asc())\

        fellows = fellows.all()
        checksum = compute_fellows_checksum(fellows)

        return render_template('fellow/panel.html', fellows=fellows, form=form, checksum=checksum)

    flash("Failed to validate request")
    fellows = []
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
        current_user.set_newsletter(NEWS_WYCINEK, form.wycinek.data)
        current_user.set_newsletter(NEWS_CONFERENCE, form.cnfrnce.data)
        current_user.set_newsletter(NEWS_ANTEOMNIA, form.anteomnia.data)
        current_user.set_newsletter(NEWS_PHOTO, form.fotki.data)
        current_user.set_newsletter(NEWS_FSZYSKO, form.fszysko.data)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('fellow.edit'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.studentid.data = current_user.studentid
        form.phone.data = current_user.phone
        form.shirt.data = current_user.shirt
        form.wycinek.data = current_user.check_newsletter(NEWS_WYCINEK)
        form.cnfrnce.data = current_user.check_newsletter(NEWS_CONFERENCE)
        form.anteomnia.data = current_user.check_newsletter(NEWS_ANTEOMNIA)
        form.fotki.data = current_user.check_newsletter(NEWS_PHOTO)
        form.fszysko.data = current_user.check_newsletter(NEWS_FSZYSKO)
    return render_template('fellow/edit.html', form=form)


@bp.cli.command("set_board")
@click.argument("email")
@click.argument("board_flag")
@click.argument("value", type=click.BOOL)
def cli_activate(email, board_flag, value):
    fellow = Fellow.query.filter_by(email=email).first()
    fellow.set_board(board_flag, value)


@bp.cli.command("get_board")
@click.argument("email")
@click.argument("board_flag")
def cli_activate(email, board_flag):
    fellow = Fellow.query.filter_by(email=email).first()
    value = fellow.check_board(board_flag)
    print(f"{value}")


@bp.cli.command("set_verified")
@click.argument("email")
@click.argument("value", type=click.BOOL)
def cli_activate(email, value):
    fellow = Fellow.query.filter_by(email=email).first()
    fellow.set_verified(value)


@bp.cli.command("get_verified")
@click.argument("email")
def cli_activate(email):
    fellow = Fellow.query.filter_by(email=email).first()
    value = fellow.verified
    print(f"{value}")

@bp.cli.command("cleardb")
def cleardb():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        log.info(f'Clear table {table}')
        db.session.execute(table.delete())
    db.session.commit()

import pandas as pnd
import secrets
from datetime import date
from lada.fellow.email import send_import_email

def random_pswd():
    return secrets.token_urlsafe(16)

@bp.cli.command("seeddb")
def seeddb():
    log.info('Seeding fellow db')
    admin = lada.fellow.register(
        email='admin@kms.uj.edu.pl',
        password='admin',
        name='Jedyny Słuszny',
        surname='Admin',
        studentid='62830',
    )

    admin.set_board(FELLOW_ACTIVE, True)
    admin.set_board(FELLOW_FELLOW, True)
    admin.set_board(FELLOW_BOARD, True)
    admin.set_board(POSITION_BOSS, True)
    admin.set_verified(True)

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

        fellow.set_board(FELLOW_ACTIVE, True)
        fellow.set_board(FELLOW_FELLOW, True)
        fellow.set_verified(True)
    db.session.commit()

@bp.cli.command("loaddb")
def loaddb():
    log.info('Importing fellow db')
    csvdb = pnd.read_csv('KMSuj_fellows.csv')
    for index, line in csvdb.iterrows():
        fellow = lada.fellow.register(
            email=line['email'],
            password=random_pswd(),
            name=line['name'],
            surname=line['surname'],
            )

        if not pnd.isnull(line['joined']):
            fellow.joined = date.fromisoformat(str(line['joined']))
            fellow.set_board(FELLOW_FELLOW, True)
        fellow.studentid = line['studentid']
        fellow.kmsid = line['kmsid']
        fellow.shirt = line['shirt']
        fellow.phone = line['phone']
        if str(fellow.email)[4:] != '@localhost.uj.edu.pl':
            send_import_email(fellow)

    db.session.commit()


@bp.cli.command("sendimportemail")
@click.argument("email")
def sendimportemail(email):
    fellow = Fellow.query.filter_by(email=email).first()
    print(fellow)
    send_import_email(fellow)
