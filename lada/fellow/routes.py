from flask import render_template, flash, url_for, redirect, request
from lada.fellow import bp
from lada.fellow.forms import LoginForm, RegisterForm, EditForm
from flask_login import current_user, login_user, logout_user, login_required
from lada.models import Fellow
from werkzeug.urls import url_parse

@bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    fellow = Fellow.query.filter_by(email=form.email.data).first()
    if fellow is None or not fellow.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('login'))
    login_user(fellow, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('index')
      return redirect(next_page)
  return render_template('fellow/login.html', form=form)

@bp.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegisterForm()
  if form.validate_on_submit():
    fellow = Fellow(email=form.email.data, name=form.name.data, surname=form.surname.data, studentid=form.studentid.data)
    fellow.set_password(form.password.data)
    db.session.add(fellow)
    db.session.commit()
    flash('Congratulations, you are now a registered fellow!')
    return redirect(url_for('login'))
  return render_template('fellow/register.html', form=form)

@bp.route('/fellow/<id>')
@login_required
def fellow(id):
  fellow = Fellow.query.filter_by(id=id).first_or_404()
  return render_template('fellow/fellow.html', fellow=fellow)

@bp.route('/edit')
@login_required
def edit():
  form = EditForm()
  if form.validate_on_submit():
    current_user.phone = form.about_me.phone
    db.session.commit()
    flash('Your changes have been saved.')
    return redirect(url_for('edit'))
  elif request.method == 'GET':
    form.about_me.phone = current_user.phone
  return render_template('fellow/edit.html', form=form)
