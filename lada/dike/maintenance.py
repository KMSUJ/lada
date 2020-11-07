import datetime
import hashlib
import logging
from copy import copy

import humanhash
from sqlalchemy import desc

from lada import db
from lada.models import Fellow, Position, Election, board_flags
from lada.constants import *
from lada.base.board import position as board, clear_board
from lada.dike.stv.ballot import Ballot
from lada.dike.stv.candidate import Candidate
from lada.dike.stv.tally import Tally

log = logging.getLogger(__name__)


def set_board(election):
    clear_board()
    log.info(f'Setting board flags after election {election}')
    boss = election.positions.filter_by(name=POSITION_BOSS).first().chosen.first()
    boss.set_board(POSITION_BOSS, True)
    boss.set_board(FELLOW_BOARD, True)
    vice = election.positions.filter_by(name=POSITION_VICE).first().chosen.first()
    vice.set_board(POSITION_VICE, True)
    treasure = election.positions.filter_by(name=POSITION_TREASURE).first().chosen.first()
    treasure.set_board(POSITION_TREASURE, True)
    secret = election.positions.filter_by(name=POSITION_SECRET).first().chosen.first()
    secret.set_board(POSITION_SECRET, True)
    library = election.positions.filter_by(name=POSITION_LIBRARY).first().chosen.first()
    library.set_board(POSITION_LIBRARY, True)
    for free in election.positions.filter_by(name=POSITION_FREE).first().chosen.all():
        free.set_board(POSITION_FREE, True)
    for covision in election.positions.filter_by(name=POSITION_COVISION).first().chosen.all():
        covision.set_board(POSITION_COVISION, True)


def get_election():
    for e in Election.query.order_by(desc(Election.id)).all():
        if e.check_flag(ELECTION_ACTIVE):
            return e
    # warn there is no election
    return None


def get_electoral(election=None, full=False):
    if election is None:
        election = get_election()
    stage_board = copy(board)
    if not full:
        if election.is_stage(STAGE_BOSS):
            stage_board = {POSITION_BOSS: 'Prezes', }
        elif election.is_stage(STAGE_BOARD):
            stage_board.pop(POSITION_BOSS)
            stage_board.pop(POSITION_COVISION)
        elif election.is_stage(STAGE_COVISION):
            stage_board = {POSITION_COVISION: 'Komisja Rewizyjna', }
    return {election.positions.filter_by(name=p).first(): election.positions.filter_by(
        name=p).first().candidates.all() for p in stage_board}


def create_positions(election):
    for p in board:
        position = Position(name=p, repname=board[p])
        db.session.add(position)
        election.add_position(position)
    db.session.commit()


def clear_positions():
    positions = Position.query.all()
    for position in positions:
        db.session.delete(position)
    db.session.commit()


def compute_fellows_checksum(fellows):
    checksum = hashlib.sha256()

    emails = [fellow.email for fellow in fellows]

    for email in sorted(emails):
        checksum.update(email.encode())

    digest = checksum.hexdigest()
    humanized = humanhash.humanize(digest, words=4)

    return humanized


def reckon_position(position):
    log.info(f'Reckoning position {position}')
    if not position.is_reckoned:
        log.info(f'Position not yet reckoned {position}')
        candidates = [Candidate(id=candidate.id) for candidate in position.candidates]
        log.debug(f'candidates = {candidates}')
        ballots = set()
        for vote in position.votes.all():
            log.debug(f'Processing vote {vote}')
            log.debug(f'vote.preference = {vote.preference}')
            log.debug(f'vote.reject = {vote.reject}')
            preference = [Candidate(id=kmsid) for kmsid in vote.preference]
            reject = {Candidate(id=kmsid) for kmsid in vote.reject}
            ballots.add(Ballot(preference, reject))
        vacancies = 1 if position.name == POSITION_BOSS else 3
        elected_candidates, discarded_candidates, rejected_candidates = Tally(ballots, vacancies,
                                                                              candidates=candidates).run()

        elected_fellows = [Fellow.query.filter_by(id=candidate.id).first() for candidate in elected_candidates]
        discarded_fellows = [Fellow.query.filter_by(id=candidate.id).first() for candidate in discarded_candidates]
        rejected_fellows = [Fellow.query.filter_by(id=candidate.id).first() for candidate in rejected_candidates]

        if position.name == POSITION_FREE:
            election = position.election
            for p in election.positions.all():
                if p.name not in (POSITION_BOSS, POSITION_FREE, POSITION_COVISION):
                    elected, _, _ = reckon_position(p)
                    elected_fellows.extend(elected)

        position.elected = elected_fellows
        position.discarded = discarded_fellows
        position.rejected = rejected_fellows
        position.is_reckoned = True
        db.session.commit()

    elected = position.elected.order_by(Fellow.surname.asc(), Fellow.name.asc()).all()
    discarded = position.discarded.order_by(Fellow.surname.asc(), Fellow.name.asc()).all()
    rejected = position.rejected.order_by(Fellow.surname.asc(), Fellow.name.asc()).all()
    return elected, discarded, rejected


def reckon_entitled_to_vote(election):
    log.info(f'Reckoning entitled fellows {election}')
    if not election.is_entitled_to_vote_reckoned:
        log.info(f'Entitled fellows not yet reckoned {election}')

        election.entitled_to_vote = Fellow.query.filter(
            Fellow.board.op('&')(board_flags[FELLOW_ACTIVE])
        ).all()
        election.is_entitled_to_vote_reckoned = True
        db.session.commit()

    entitled = election.entitled_to_vote.order_by(Fellow.surname.asc(), Fellow.name.asc()).all()
    return entitled


def verify_voters(election):
    result = True

    entitled_ids = {entitled.id for entitled in reckon_entitled_to_vote(election)}
    voters = [voter for voter in election.voters_boss] + [voter for voter in election.voters_board] + [voter for voter in election.voters_covision]
    for voter in voters:
        log.debug(f"Legal voter detected: {voter}")
        if voter.id not in entitled_ids:
            log.warning(f"Illegal voter detected: {voter}")
            result = False

    return result


def reckon_election(election):
    log.info(f'Reckoning election {election}')
    results = list()
    positions = [position for position in election.positions.all() if position.name in POSITIONS[election.stage]]
    for position in positions:
        elected, discarded, rejected = reckon_position(position)
        results.append({'position': position,
                        'elected': elected,
                        'discarded': discarded,
                        'rejected': rejected,
                        })
    entitled = reckon_entitled_to_vote(election)
    log.info(f'Election results: {results}')
    return results, entitled

  
def store_chosen(election, form):
    log.info(f'Storing candidates chosen for board positions.')
    vice = Fellow.query.filter_by(id=form.vice.data).first()
    election.positions.filter_by(name=POSITION_VICE).first().choose(vice)
    election.positions.filter_by(name=POSITION_COVISION).first().unregister(vice)
    treasure = Fellow.query.filter_by(id=form.treasure.data).first()
    election.positions.filter_by(name=POSITION_TREASURE).first().choose(treasure)
    election.positions.filter_by(name=POSITION_COVISION).first().unregister(treasure)
    secret = Fellow.query.filter_by(id=form.secret.data).first()
    election.positions.filter_by(name=POSITION_SECRET).first().choose(secret)
    election.positions.filter_by(name=POSITION_COVISION).first().unregister(secret)
    library = Fellow.query.filter_by(id=form.library.data).first()
    election.positions.filter_by(name=POSITION_LIBRARY).first().choose(library)
    election.positions.filter_by(name=POSITION_COVISION).first().unregister(library)
    frees = form.free.data.split("+")
    if '' in frees:
        frees.remove('')
    if frees is not None:
        for j in frees:
            free = Fellow.query.filter_by(id=j).first()
            election.positions.filter_by(name=POSITION_FREE).first().choose(free)
            election.positions.filter_by(name=POSITION_COVISION).first().unregister(free)
    db.session.commit()


def begin_election():
    log.info('Starting election')
    election = Election(year=datetime.datetime.utcnow().year)
    election.set_flag(ELECTION_ACTIVE, True)
    db.session.add(election)
    create_positions(election)
    begin_registration(election)
    db.session.commit()


def begin_registration(election):
    log.info('Opening registration')
    election.set_flag(ELECTION_REGISTER, True)
    db.session.commit()


def begin_voting(election):
    if election.stage not in ELECTION_STAGES:
        log.warning("Election doeas not have a set stage.")
    log.info(f"Starting voting at stage: {election.stage}")
    election.set_flag(ELECTION_REGISTER, False)
    election.set_flag(ELECTION_VOTING, True)
    db.session.commit()


def end_voting(election):
    log.info("Ending voting")
    election.set_flag(ELECTION_VOTING, False)
    db.session.commit()


def end_election(election):
    election.set_flag(ELECTION_ACTIVE, False)
    db.session.commit()
