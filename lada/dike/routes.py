from operator import itemgetter
from flask import render_template, flash, url_for, redirect, request
from lada import db
from lada.dike import bp
from flask_login import current_user, login_required, logout_user
from lada.dike.forms import RegisterForm, BallotForm, PanelForm, AfterBallotForm
from wtforms import HiddenField
from lada.models import Fellow, Position, Vote
from lada.fellow.board import position, board_required
import lada.dike.maintenance as mn

def register_candidate(form, election):
  fellow = Fellow.query.filter_by(id=form.studentid.data).first()
  if fellow is None:
    return None # raise some exception or whatevs
  for p in position:
    if getattr(getattr(form, f'{p}'), 'data'):
      election.positions.filter_by(name=position[p]).first().register(fellow)
  db.session.commit()

def store_votes(form, electoral):
  ballot = list()
  for field in form.data:
    if "+" in field:
      name = field.split("+")
      ballot.append({'pos':int(name[0]), 'cnd':int(name[1]), 'val':form.data[field]})
  
  for position in electoral:
    position.store_vote(Vote(
      reject = {line['cnd'] for line in ballot if line['pos']==position.id and line['val']=='x'},
      preference = [int(line['cnd']) for line in sorted([line for line in ballot if line['pos']==position.id and line['val'] not in {'x','n'}], key=itemgetter('val'))]
      ))
  db.session.commit()

@bp.route('/register', methods=['GET', 'POST'])
@board_required(['board', 'covision'])
@login_required
def register():
  election = mn.get_election()
  if election is None:
    flash(f'Wybory nie są aktywne.')
    return redirect(url_for('base.index'))
  elif not election.check_flag('register'):
    flash(f'Rejestracja nie jest aktywna')
    return redirect(url_for('base.index'))
  
  form = RegisterForm()
  if form.validate_on_submit():
    if current_user.check_password(form.password.data):
      # check if candidate is already registered
      register_candidate(form, election)
      flash('Kandydat zarejestrowany poprawnie.')
      return redirect(url_for('base.index'))
    else:
      flash('Podane hasło jest niepoprawne.')
  return render_template('dike/register.html', form=form)

@bp.route('/ballot', methods=['GET', 'POST'])
@login_required
def ballot():
  election = mn.get_election()
  if election is None:
    flash(f'Wybory nie są aktywne.')
    return redirect(url_for('base.index'))
  elif not election.check_flag('voting'):
    flash(f'Głosowanie nie jest aktywne.')
    return redirect(url_for('base.index'))
  
  if election.did_vote(current_user):
    flash(f'Oddano już głos w tych wyborach.')
    return redirect(url_for('base.index'))
  
  electoral = mn.get_electoral(election)
  class DynamicBallotForm(BallotForm):
    pass
  for position in electoral:
    for candidate in electoral[position]:
      setattr(DynamicBallotForm, f'{position.id}+{candidate.id}', HiddenField(default="n"))

  form = DynamicBallotForm()
  if form.validate_on_submit():
    if current_user.check_password(form.password.data):
      store_votes(form, electoral)
      election.add_voter(current_user)
      flash('Głos oddany poprawnie.')
      return redirect(url_for('dike.afterballot'))
    else:
      flash('Podane hasło jest niepoprawne.')
  return render_template('dike/ballot.html', form=form, electoral=electoral)

@bp.route('/afterballot', methods=['GET', 'POST'])
def afterballot():
  form = AfterBallotForm()
  if form.validate_on_submit():
    logout_user()
    return redirect(url_for('dike.ballot'))
  return render_template('dike/afterballot.html', form=form)

# delete later
import random as rnd

@bp.route('seedregister')
def seedregister():
  election = mn.get_election()
  for fellow in Fellow.query.all():
    form = RegisterForm()
    form.studentid.data = fellow.studentid
    form.boss.data, form.vice.data, form.treasure.data, form.library.data, form.secret.data, form.free.data, form.covision.data = rnd.choices([False, True], weights=[5,2], k=7)
    register_candidate(form, election)
  flash('Register Seeded')
  return redirect(url_for('dike.panel'))

@bp.route('seedvote')
def seedvote():
  electoral = mn.get_electoral(mn.get_election())
  class DynamicBallotForm(BallotForm):
    pass
  for position in electoral:
    for candidate in electoral[position]:
      setattr(DynamicBallotForm, f'{position.id}+{candidate.id}', HiddenField(default="n"))

  for i in range(144):
    form = DynamicBallotForm()
    for position in electoral:
      j = 1
      rnd.shuffle(electoral[position])
      for candidate in electoral[position]:
        if rnd.random() < 0.3:
          k = 'x'
        elif rnd.random() < 0.3:
          k = 'n'
        else:
          k = j
          j += 1
        setattr(getattr(form, f'{position.id}+{candidate.id}'), 'data', k)
    store_votes(form, electoral)
  return redirect(url_for('dike.panel'))

@bp.route('reckon')
def reckon():
  election = mn.get_election()
  mn.reckon_election(election)
  flash('reckoned')
  return redirect(url_for('dike.panel'))

# end delete

@bp.route('/panel', methods=['GET', 'POST'])
@board_required(['board', 'covision'])
@login_required
def panel():
  election = mn.get_election()
  form = PanelForm()
  if election is None:
    if form.validate_on_submit():
      mn.begin_election()
      flash(f'Rozpoczęto wybory.')
      return redirect(url_for('dike.panel'))
    return render_template('dike/panel.html', form=form, mode='inactive')
  elif election.check_flag('register'):
    if form.validate_on_submit():
      mn.begin_voting(election)
      flash(f'Rozpoczęto głosowanie.')
      return redirect(url_for('dike.panel'))
    return render_template('dike/panel.html', form=form, mode='register', electoral=mn.get_electoral(election))
  elif election.check_flag('voting'):
    if form.validate_on_submit():
      mn.end_voting(election)
      flash('Zakończono głosowanie.')
      #redirect to select board from voting results
      return redirect(url_for('dike.panel'))
    return render_template('dike/panel.html', form=form, mode='voting')
  else:
    if form.validate_on_submit():
      mn.end_election(election)
      flash(f'Zakończono Wybory.')
      return redirect(url_for('dike.panel'))
    return render_template('dike/panel.html', form=form, mode='endscreen')
