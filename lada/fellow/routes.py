import datetime
from flask import render_template, flash, url_for, redirect, request
from lada import db
from lada.fellow import bp
from lada.fellow.forms import LoginForm, RegisterForm, EditForm, AdressForm, InitiateForm
from wtforms import BooleanField
from flask_login import current_user, login_user, logout_user, login_required
from lada.models import Fellow
from werkzeug.urls import url_parse

@bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('base.index'))
  form = LoginForm()
  if form.validate_on_submit():
    fellow = Fellow.query.filter_by(email=form.email.data).first()
    if fellow is None or not fellow.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('fellow.login'))
    login_user(fellow, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
      next_page = url_for('base.index')
      return redirect(next_page)
  return render_template('fellow/login.html', form=form)

@bp.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('base.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('base.index'))
  form = RegisterForm()
  if form.validate_on_submit():
    fellow = Fellow(email=form.email.data, name=form.name.data, surname=form.surname.data, studentid=form.studentid.data, newsletter=0)
    fellow.set_password(form.password.data)
    db.session.add(fellow)
    db.session.commit()
    flash('Reigistration successful.')
    return redirect(url_for('fellow.login'))
  return render_template('fellow/register.html', form=form)

def activate(fellow, value=True):
  if value and not fellow.check_board('fellow'):
    fellow.joined = datetime.datetime.utcnow()
    fellow.set_board('fellow', True)
  fellow.set_board('active', value)
  return

@bp.route('/view/<id>', methods=['GET', 'POST'])
@login_required
def view(id):
  form = InitiateForm()
  fellow = Fellow.query.filter_by(id=id).first_or_404()
  if form.validate_on_submit():
    activate(fellow)
    db.session.commit()
  return render_template('fellow/fellowid.html', fellow=fellow, form=form)

# delete this later
@bp.route('/cleardb')
def cleardb():
  meta = db.metadata
  for table in reversed(meta.sorted_tables):
    print(f'Clear table {table}')
    db.session.execute(table.delete())
  db.session.commit()
  flash(f'Database Clear')
  return redirect(url_for('fellow.register'))

@bp.route('/seeddb')
def seeddb():
  admin = Fellow(email='admin@kms.uj.edu.pl', name = 'Jedyny Słuszny', surname = 'Admin', studentid = '62830')
  admin.set_password('admin')
  db.session.add(admin)
  admin.set_board('active', True)
  admin.set_board('fellow', True)
  admin.joined = datetime.datetime.utcnow()
  admin.set_board('board', True)
  admin.set_board('president', True)

  names = {'Adrian', 'Zofia', 'Baltazar', 'Weronika', 'Cezary', 'Urszula', 'Dominik', 'Telimena', 'Euzebiusz', 'Sabrina', 'Filemon', 'Roksana', 'Grzegorz', 'Patrycja', 'Henryk', 'Ofelia', 'Iwan', 'Nina', 'Jeremiasz', 'Monika', 'Klaus', 'Laura'}
  surs = {'Albinos', 'Bzykała', 'Cyc', 'Debil', 'Ekler', 'Fiut', 'Gbur', 'Hałas', 'Imbecyl', 'Jebaka', 'Kutas', 'Lewak', 'Mikrus', 'Nygus', 'Odbyt', 'Przechuj', 'Ruchała', 'Skurwiel', 'Trzmiel', 'Ubek', 'Wrotek', 'Zlew'}
  for i,p in enumerate(zip(names, surs)):
    fellow = Fellow(
        email = f'{p[1].lower()}.{p[0].lower()}@kms.uj.edu.pl',
        name = p[0],
        surname = p[1],
        studentid = i
        )
    fellow.set_password(f'{p[0]}{i}{p[1]}')
    fellow.set_board('active', True)
    fellow.set_board('fellow', True)
    fellow.joined = datetime.datetime.utcnow()
    db.session.add(fellow)
  db.session.commit()
  flash(f'Database Seeded')
  return redirect(url_for('base.index'))
# end delete

@bp.route('/panel', methods=['GET', 'POST'])
@login_required
def panel():
  if current_user.check_board('president') or current_user.check_board('vice') or current_user.check_board('treasurer'):
    fellows = Fellow.query.all()
    class InitiateMultipleForm(InitiateForm):
      pass

    for fellow in fellows:
      setattr(InitiateMultipleForm, f'{fellow.id}', BooleanField('Active'))
    form = InitiateMultipleForm()
    if form.validate_on_submit():
      for fellow in fellows:
        activate(fellow, getattr(getattr(form, f'{fellow.id}'), 'data'))
      db.session.commit()
      flash('Your changes have been saved.')
      return redirect(url_for('fellow.panel'))
    elif request.method == 'GET':
      for fellow in fellows:
        setattr(getattr(form, f'{fellow.id}'), 'data', fellow.check_board('active'))
      return render_template('fellow/panel.html', fellows=fellows, form=form)
  else:
    flash('You do not have access to this site.')
    return redirect(url_for('base.index'))

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
  return render_template('fellow/edit.html', form=form)
