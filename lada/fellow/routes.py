import logging

import click
import flask_featureflags as feature
from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

import lada.fellow
from lada import db
from lada.models import Fellow
from lada.constants import *
from lada.fellow import bp
from lada.fellow.email import send_password_reset_email, send_verification_email
from lada.fellow.forms import LoginForm, PasswordResetRequestForm, PasswordResetForm

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


""" maybe can be used to supplement the cli
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('base.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        fellow = lada.fellow.register(
            email=form.email.data,
            password=form.password.data,
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
@login_required
def panel():
    form = PanelForm(meta={'csrf': False}, formdata=request.args)
    if form.validate():
        fellows = Fellow.query

        if form.active.data:
            fellows = fellows.filter(
                Fellow.board.op('&')(board_flags[FELLOW_ACTIVE])
            )

        fellows = fellows.all()
        checksum = compute_fellows_checksum(fellows)

        return render_template('fellow/panel.html', fellows=fellows, form=form)

    flash("Failed to validate request")
    fellows = []
    return render_template('fellow/panel.html', fellows=fellows, form=form)
"""


# cli

## creating fellows

@bp.cli.command("register_fellow")
@click.argument("email")
@click.argument("password")
def cli_register(email, password):
    # should probably ask for password twice
    # moreover should not provide password as an argument but instead ask for it in some secure way
    # to be improved
    fellow = lada.fellow.register(
        email=email,
        password=password,
        )
    log.info(f"New fellow registered: {fellow}")
    if feature.is_active(FEATURE_EMAIL_VERIFICATION):
        send_verification_email(fellow)
        print('Registration successful. Please check your e-mail, including SPAM, for verification e-mail.')
    else:
        fellow.set_verified(True)
        print('Registration successful.')


## flags

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


@bp.cli.command("set_admin")
@click.argument("email")
@click.argument("value", type=click.BOOL)
def cli_activate(email, value):
    fellow = Fellow.query.filter_by(email=email).first()
    fellow.set_admin(value)

@bp.cli.command("get_admin")
@click.argument("email")
@click.argument("board_flag")
def cli_activate(email):
    fellow = Fellow.query.filter_by(email=email).first()
    value = fellow.check_admin()
    print(f"{value}")


@bp.cli.command("set_redactor")
@click.argument("email")
@click.argument("value", type=click.BOOL)
def cli_activate(email, value):
    fellow = Fellow.query.filter_by(email=email).first()
    fellow.set_redactor(value)

@bp.cli.command("get_redactor")
@click.argument("email")
@click.argument("board_flag")
def cli_activate(email):
    fellow = Fellow.query.filter_by(email=email).first()
    value = fellow.check_redactor()
    print(f"{value}")


## demo

@bp.cli.command("cleardb")
def cleardb():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        log.info(f'Clear table {table}')
        db.session.execute(table.delete())
    db.session.commit()
