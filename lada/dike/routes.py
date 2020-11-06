import logging
from operator import itemgetter

import flask_featureflags as feature
from flask import render_template, flash, url_for, redirect
from flask_login import current_user, login_required, logout_user
from wtforms import HiddenField

from lada import db
from lada.models import Fellow, Vote, Position
from lada.constants import *
from lada.base.board import position, board_required, active_required, get_board
from lada.dike import bp
from lada.dike import maintenance
from lada.dike.forms import RegisterForm, BallotForm, PanelForm, AfterBallotForm, ReckoningFormBoss, ReckoningFormBoard, ReckoningFormCovision, EndscreenForm, ArbitraryDiscardDecisionForm
from lada.dike.maintenance import compute_fellows_checksum, reckon_entitled_to_vote, verify_voters, ArbitraryDiscardDecisionNeededError

log = logging.getLogger(__name__)


def register_candidate(form, election):
    fellow = Fellow.query.filter_by(id=form.kmsid.data).first()
    if fellow is None:
        return None  # raise some exception or whatevs
    for p in position:
        if getattr(getattr(form, f'{p}'), 'data'):
            election.positions.filter_by(name=p).first().register(fellow)
    db.session.commit()


def unregister_candidates(form, election):
    for field in form.data:
        if "+" in field and form.data[field] == 'x':
            name = field.split("+")
            election.positions.filter_by(id=int(name[0])).first().unregister(Fellow.query.filter_by(id=int(name[1])).first())
    db.session.commit()


def store_votes(form, electoral):
    ballot = list()
    for field in form.data:
        if "+" in field:
            name = field.split("+")
            ballot.append({'pos': int(name[0]), 'cnd': int(name[1]), 'val': form.data[field]})

    for position in electoral:
        reject = {
            line['cnd']
            for line in ballot
            if line['pos'] == position.id and line['val'] == 'x'
        }

        preference_lines = [line for line in ballot if line['pos'] == position.id and line['val'] not in ('x', 'n')]
        preference_lines = sorted(preference_lines, key=itemgetter('val'))
        preference = [int(line['cnd']) for line in preference_lines]

        position.store_vote(Vote(
            reject=reject,
            preference=preference
        ))
    db.session.commit()


@bp.route('/register', methods=['GET', 'POST'])
@board_required(POSITIONS_ALL)
@login_required
def register():
    election = maintenance.get_election()
    if election is None:
        flash(f'Wybory nie są aktywne.')
        return redirect(url_for('base.index'))
    elif not election.check_flag(ELECTION_REGISTER):
        flash(f'Rejestracja nie jest aktywna')
        return redirect(url_for('base.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            kmsid = form.kmsid.data
            log.debug(f'Trying to register candidate by kms id: {kmsid}')
            fellow = Fellow.query.filter_by(id=kmsid).first()
            log.info(f'Trying to register candidate: {fellow}')
            
            if not fellow.check_board(FELLOW_ACTIVE):
                log.warning(f'Candidate is not an active fellow: {fellow}.')
                flash(f'Kandydat nie jest aktywnym członkiem.')
                return redirect(url_for('base.index'))

            for position in election.positions.all():
                if position.is_registered(fellow):
                    log.warning(f'Candidate is already registered: {fellow}')
                    flash('Kandydat został już zarejestrowany.')
                    return redirect(url_for('base.index'))

            register_candidate(form, election)
            log.info(f'New candidate registered: {fellow}')
            flash('Kandydat zarejestrowany poprawnie.')
            return redirect(url_for('base.index'))
        else:
            flash('Podane hasło jest niepoprawne.')
    return render_template('dike/register.html', form=form)


@bp.route('/ballot', methods=['GET', 'POST'])
@login_required
def ballot():
    election = maintenance.get_election()
    if election is None:
        flash(f'Wybory nie są aktywne.')
        return redirect(url_for('base.index'))
    elif not election.check_flag(ELECTION_VOTING):
        flash(f'Głosowanie nie jest aktywne.')
        return redirect(url_for('base.index'))

    if not election.is_entitled_to_vote(current_user):
        flash(f'Nie masz prawa wyborczego w tych wyborach.')
        return redirect(url_for('base.index'))

    if election.did_vote(current_user):
        flash(f'Oddano już głos w tych wyborach.')
        return redirect(url_for('base.index'))

    electoral = maintenance.get_electoral(election)

    class DynamicBallotForm(BallotForm):
        pass

    for position in electoral:
        for candidate in electoral[position]:
            setattr(DynamicBallotForm, f'{position.id}+{candidate.id}', HiddenField(default="n"))

    form = DynamicBallotForm()
    if form.validate_on_submit():
        store_votes(form, electoral)
        election.add_voter(current_user)
        db.session.commit()
        log.info('New ballot received')
        flash('Głos oddany poprawnie.')
        return redirect(url_for('dike.afterballot'))
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
@feature.is_active_feature(FEATURE_DEMO)
def seedregister():
    log.info("Seeding registration")
    election = maintenance.get_election()
    for fellow in Fellow.query.all():
        form = RegisterForm()
        form.kmsid.data = fellow.studentid
        form.boss.data, form.vice.data, form.treasure.data, form.library.data, form.secret.data, form.free.data, form.covision.data = rnd.choices(
            [False, True], weights=[5, 2], k=7)
        register_candidate(form, election)
    flash('Register Seeded')
    return redirect(url_for('dike.panel'))


@bp.route('seedvote')
@feature.is_active_feature(FEATURE_DEMO)
def seedvote():
    log.info("Seeding votes")
    electoral = maintenance.get_electoral(maintenance.get_election())

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
@feature.is_active_feature(FEATURE_DEMO)
def reckon():
    election = maintenance.get_election()
    maintenance.reckon_election(election)
    flash('reckoned')
    return redirect(url_for('dike.panel'))


# end delete

@bp.route('/reckoning', methods=['GET', 'POST'])
@board_required(POSITIONS_ALL + [FELLOW_BOARD])
@login_required
def reckoning():
    election = maintenance.get_election()
    if not (not (election is None) and not election.check_flag(ELECTION_REGISTER)):
        flash(f'Głosowanie nie jest aktywne.')
    elif election.check_flag(ELECTION_VOTING):
        flash(f'Głosowanie nie zostało zakończone.')

    if not verify_voters(election):
        flash('Illegal voter detected')

    try:
        results, entitled = maintenance.reckon_election(election)
    except ArbitraryDiscardDecisionNeededError as e:
        form = ArbitraryDiscardDecisionForm()
        form.position.data = e.position.id
        return render_template('dike/arbitrary_discard_decision.html', form=form, election=e.election, position=e.position, candidates=e.candidates)

    checksum = compute_fellows_checksum(entitled)
    
    if election.is_stage(STAGE_BOSS):

        form = ReckoningFormBoss()
        if form.validate_on_submit():
            boss = results[0]['elected'][0]
            election.positions.filter_by(name=POSITION_BOSS).first().choose(boss)
            for position in election.positions.filter(Position.name != POSITION_BOSS).all():
                position.unregister(boss)
            maintenance.begin_registration(election)
            return redirect(url_for('dike.panel'))
        return render_template('dike/reckoning.html', form=form, results=results, checksum=checksum, stage=election.stage)

    elif election.is_stage(STAGE_BOARD):
        form = ReckoningFormBoard()
        if form.validate_on_submit():
            maintenance.store_chosen(election, form)
            maintenance.begin_registration(election)
            return redirect(url_for('dike.panel'))
        return render_template('dike/reckoning.html', form=form, results=results, checksum=checksum, stage=election.stage)

    elif election.is_stage(STAGE_COVISION):
        form = ReckoningFormCovision()
        if form.validate_on_submit():
            for covision in results[0]['elected']:
                election.positions.filter_by(name=POSITION_COVISION).first().choose(covision)
            maintenance.set_board(election)
            return redirect(url_for('dike.endscreen'))
        return render_template('dike/reckoning.html', form=form, results=results, checksum=checksum, stage=election.stage)


@bp.route('/endscreen', methods=['GET', 'POST'])
@board_required(POSITIONS_ALL + [FELLOW_BOARD])
@login_required
def endscreen():
    election = maintenance.get_election()
    if not (not (election is None) and not election.check_flag(ELECTION_REGISTER)):
        flash(f'Głosowanie nie jest aktywne.')
    elif election.check_flag(ELECTION_VOTING):
        flash(f'Głosowanie nie zostało zakończone.')
    
    if not verify_voters(election):
        flash('Illegal voter detected')

    board = get_board() 
    _, entitled = maintenance.reckon_election(election) 
    checksum = compute_fellows_checksum(entitled)
    
    form = EndscreenForm()
    if form.validate_on_submit():
        maintenance.end_election(election)
        return redirect(url_for('base.board'))

    return render_template('dike/endscreen.html', form=form, board=board, checksum=checksum)


@bp.route('/arbitrary_discard_decisions', methods=['POST'])
@board_required(POSITIONS_ALL + [FELLOW_BOARD])
@login_required
def arbitrary_discard_decisions():
    form = ArbitraryDiscardDecisionForm()

    position_id = int(form.position.data)
    position = Position.query.filter_by(id=position_id).first()

    fellow_ids = [int(i) for i in form.candidates.data.split("+")]
    fellows = [Fellow.query.filter_by(id=i).first() for i in fellow_ids]

    position.append_arbitrary_discard(fellows)

    return redirect(url_for('dike.reckoning'))


@bp.route('/panel', methods=['GET', 'POST'])
@board_required(POSITIONS_ALL + [FELLOW_BOARD])
@login_required
def panel():
    election = maintenance.get_election()
    form = PanelForm()
    log.debug('Dike panel opened')
    if election is None:
        if form.validate_on_submit():
            maintenance.begin_election()
            flash(f'Rozpoczęto wybory.')
            return redirect(url_for('dike.panel'))
        return render_template('dike/panel.html', form=form, mode='inactive')
    
    elif election.check_flag(ELECTION_REGISTER):
        class DynamicPanelForm(PanelForm):
            pass

        electoral = maintenance.get_electoral(election, full=True)
        for position in electoral:
            for candidate in electoral[position]:
                setattr(DynamicPanelForm, f'{position.id}+{candidate.id}', HiddenField(default="n"))

        form = DynamicPanelForm()
        if form.validate_on_submit():
            if form.unregister_candidates.data:
                unregister_candidates(form, election)
                return redirect(url_for('dike.panel'))

            if form.begin_voting_boss.data:
                election.set_stage(STAGE_BOSS)
            elif form.begin_voting_board.data:
                election.set_stage(STAGE_BOARD)
            elif form.begin_voting_covision.data:
                election.set_stage(STAGE_COVISION)
            maintenance.begin_voting(election)
            flash(f'Rozpoczęto głosowanie.')
            return redirect(url_for('dike.panel'))
        return render_template('dike/panel.html', form=form, mode='register',
                               electoral=electoral)

    elif election.check_flag(ELECTION_VOTING):
        if form.validate_on_submit():
            maintenance.end_voting(election)
            flash('Zakończono głosowanie.')
            return redirect(url_for('dike.reckoning'))

        if not verify_voters(election):
            flash('Illegal voter detected')

        log.debug(f"election.voters_boss.all() = {election.voters_boss.all()}")
        log.debug(f"election.voters_board.all() = {election.voters_board.all()}")
        log.debug(f"election.voters_covision.all() = {election.voters_covision.all()}")
        log.debug(f"election.did_vote({current_user}) = {election.did_vote(current_user)}")

        entitled = reckon_entitled_to_vote(election)
        entitled_checksum = compute_fellows_checksum(entitled)

        return render_template('dike/panel.html', form=form, mode='voting', count=election.count_votes(), entitled_checksum=entitled_checksum)
    
    else:
        return redirect(url_for('dike.reckoning'))
