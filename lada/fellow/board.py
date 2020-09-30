import functools

from flask import flash, redirect, url_for
from flask_login import current_user

from lada.constants import *
from lada.models import Fellow, board_flags

position = {
    POSITION_BOSS: 'Prezes',
    POSITION_VICE: 'Wiceprezes',
    POSITION_TREASURE: 'Skarbnik',
    POSITION_SECRET: 'Sekretarz',
    POSITION_LIBRARY: 'Bibiotekarz',
    POSITION_FREE: 'Wolny Członek',
    POSITION_COVISION: 'Komisja Rewizyjna',
}


def board_required(position):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):

            if current_user.is_authenticated and current_user.is_board(*position):
                value = function(*args, **kwargs)
                return value
            else:
                flash('You do not have acess to this site.')
                return redirect(url_for('base.index'))

        return wrapper

    return decorator


def get_board():
    return {
        POSITION_BOSS: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_BOSS]) == board_flags[POSITION_BOSS]).first(),
        POSITION_VICE: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_VICE]) == board_flags[POSITION_VICE]).first(),
        POSITION_TREASURE: Fellow.query.filter(
            Fellow.board.op('&')(board_flags[POSITION_TREASURE]) == board_flags[POSITION_TREASURE]).first(),
        POSITION_SECRET: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_SECRET]) == board_flags[POSITION_SECRET]).first(),
        POSITION_LIBRARY: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_LIBRARY]) == board_flags[POSITION_LIBRARY]).first(),
        POSITION_FREE: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_FREE]) == board_flags[POSITION_FREE]).all(),
        POSITION_COVISION: Fellow.query.filter(
            Fellow.board.op('&')(board_flags[POSITION_COVISION]) == board_flags[POSITION_COVISION]).all(), }


def clear_board():
    for fellow in Fellow.query.filter(Fellow.board.op('&')(board_flags[FELLOW_BOARD]) == board_flags[FELLOW_BOARD]).all():
        fellow.set_board(FELLOW_BOARD, False)
        fellow.set_board(POSITION_BOSS, False)
        fellow.set_board(POSITION_VICE, False)
        fellow.set_board(POSITION_TREASURE, False)
        fellow.set_board(POSITION_SECRET, False)
        fellow.set_board(POSITION_LIBRARY, False)
        fellow.set_board(POSITION_FREE, False)

    for fellow in Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_COVISION]) == board_flags[POSITION_COVISION]).all():
        fellow.set_board(POSITION_COVISION, False)
