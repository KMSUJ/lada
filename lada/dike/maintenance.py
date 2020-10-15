import datetime
import hashlib
import logging

import humanhash
from sqlalchemy import desc

from lada import db
from lada.dike.stv.ballot import Ballot
from lada.dike.stv.candidate import Candidate
from lada.dike.stv.tally import Tally
from lada.fellow.board import position as board, clear_board
from lada.constants import *
from lada.models import Fellow, Position, Election, board_flags

log = logging.getLogger(__name__)


def set_board(form):
    clear_board()
    boss = Fellow.query.filter_by(id=form.boss.data).first()
    boss.set_board(FELLOW_BOARD, True)
    boss.set_board(POSITION_BOSS, True)
    vice = Fellow.query.filter_by(id=form.vice.data).first()
    vice.set_board(FELLOW_BOARD, True)
    vice.set_board(POSITION_VICE, True)
    treasure = Fellow.query.filter_by(id=form.treasure.data).first()
    treasure.set_board(FELLOW_BOARD, True)
    treasure.set_board(POSITION_TREASURE, True)
    secret = Fellow.query.filter_by(id=form.secret.data).first()
    secret.set_board(FELLOW_BOARD, True)
    secret.set_board(POSITION_SECRET, True)
    library = Fellow.query.filter_by(id=form.library.data).first()
    library.set_board(FELLOW_BOARD, True)
    library.set_board(POSITION_LIBRARY, True)
    frees = form.free.data.split("+")
    if '' in frees:
        frees.remove('')
    if frees is not None:
        for j in frees:
            free = Fellow.query.filter_by(id=j).first()
            free.set_board(FELLOW_BOARD, True)
            free.set_board(POSITION_FREE, True)
    for j in form.covision.data.split("+"):
        covision = Fellow.query.filter_by(id=j).first()
        covision.set_board(POSITION_COVISION, True)


def get_election():
    for e in Election.query.order_by(desc(Election.id)).all():
        if e.check_flag(ELECTION_ACTIVE):
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


def reckon_election(election):
    log.info(f'Reckoning election {election}')
    results = list()
    for position in election.positions.all():
        elected, discarded, rejected = reckon_position(position)
        results.append({'position': position,
                        'elected': elected,
                        'discarded': discarded,
                        'rejected': rejected,
                        })
    entitled = reckon_entitled_to_vote(election)
    log.info(f'Election results: {results}')
    return results, entitled


def begin_election():
    log.info('Starting election')
    election = Election(year=datetime.datetime.utcnow().year)
    election.set_flag(ELECTION_ACTIVE, True)
    db.session.add(election)
    create_positions(election)
    election.set_flag(ELECTION_REGISTER, True)
    db.session.commit()


def begin_voting(election):
    log.info("Starting voting")
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
