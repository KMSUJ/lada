import datetime
import logging

from sqlalchemy import desc

from lada import db
from lada.dike.stv.ballot import Ballot
from lada.dike.stv.candidate import Candidate
from lada.dike.stv.tally import Tally
from lada.fellow.board import position as board, clear_board
from lada.models import Fellow, Position, Election

log = logging.getLogger(__name__)


def set_board(form):
    clear_board()
    boss = Fellow.query.filter_by(id=form.boss.data).first()
    boss.set_board('board', True)
    boss.set_board('boss', True)
    vice = Fellow.query.filter_by(id=form.vice.data).first()
    vice.set_board('board', True)
    vice.set_board('vice', True)
    treasure = Fellow.query.filter_by(id=form.treasure.data).first()
    treasure.set_board('board', True)
    treasure.set_board('treasure', True)
    secret = Fellow.query.filter_by(id=form.secret.data).first()
    secret.set_board('board', True)
    secret.set_board('secret', True)
    library = Fellow.query.filter_by(id=form.library.data).first()
    library.set_board('board', True)
    library.set_board('library', True)
    frees = form.free.data.split("+")
    if '' in frees:
        frees.remove('')
    if frees is not None:
        for j in frees:
            free = Fellow.query.filter_by(id=j).first()
            free.set_board('board', True)
            free.set_board('free', True)
    for j in form.covision.data.split("+"):
        covision = Fellow.query.filter_by(id=j).first()
        covision.set_board('covision', True)


def get_election():
    for e in Election.query.order_by(desc(Election.id)).all():
        if e.check_flag('active'):
            return e
    # warn there is no election
    return None


def get_electoral(election=None):
    if election is None:
        election = get_election()
    return {election.positions.filter_by(name=p).first(): election.positions.filter_by(
        name=p).first().candidates.all() for p in board}


def create_positions(election):
    for p in board:
        position = Position(name=p, flagname=p)
        db.session.add(position)
        election.add_position(position)
    db.session.commit()


def clear_positions():
    positions = Position.query.all()
    for position in positions:
        db.session.delete(position)
    db.session.commit()


def reckon_position(position):
    log.info(f'Reckoning position {position}')
    ballots = set()
    for vote in position.votes.all():
        log.debug(f'Processing vote {vote}')
        log.debug(f'vote.preference = {vote.preference}')
        log.debug(f'vote.reject = {vote.reject}')
        preference = [Candidate(id=kmsid) for kmsid in vote.preference]
        reject = {Candidate(id=kmsid) for kmsid in vote.reject}
        ballots.add(Ballot(preference, reject))
    vacancies = 1 if position.name == 'boss' else 3
    return Tally(ballots, vacancies).run()


def reckon_election(election):
    log.info(f'Reckoning election {election}')
    results = list()
    for position in election.positions.all():
        elected, discarded, rejected = reckon_position(position)
        results.append({'position': position,
                        'elected': [Fellow.query.filter_by(id=candidate.id).first() for candidate in elected],
                        'discarded': [Fellow.query.filter_by(id=candidate.id).first() for candidate in
                                      reversed(discarded)],
                        'rejected': [Fellow.query.filter_by(id=candidate.id).first() for candidate in rejected], })
    log.info(f'Election results: {results}')
    return results


def begin_election():
    log.info('Starting election')
    election = Election(year=datetime.datetime.utcnow().year)
    election.set_flag('active', True)
    db.session.add(election)
    create_positions(election)
    election.set_flag('register', True)
    db.session.commit()


def begin_voting(election):
    log.info("Starting voting")
    election.set_flag('register', False)
    election.set_flag('voting', True)
    db.session.commit()


def end_voting(election):
    log.info("Ending voting")
    election.set_flag('voting', False)
    db.session.commit()


def end_election(election):
    election.set_flag('active', False)
    db.session.commit()
