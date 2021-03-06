import functools

from flask import flash, redirect, url_for, request, current_app
from flask_login import current_user
from flask_login.config import EXEMPT_METHODS

from lada import db
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


def is_admin():
  return current_user.is_board(FELLOW_BOARD) or current_user.is_board(POSITION_BOSS) or current_user.is_board(POSITION_VICE)

def board_required(position):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):

            if current_user.is_authenticated and (is_admin() or current_user.is_board(*position)):
                value = function(*args, **kwargs)
                return value
            else:
                flash('You do not have acess to this site.')
                return redirect(url_for('base.index'))

        return wrapper

    return decorator


def active_required(function):
    @functools.wraps(function)
    def decorator(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return function(*args, **kwargs)
        elif current_app.config.get('LOGIN_DISABLED'):
            return function(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.check_board(FELLOW_ACTIVE):
            current_app.logger.warning(f'Voter is not an active fellow: {current_user}.')
            flash('Musisz być aktywnym członkiem.')
            return redirect(url_for('base.index'))
        return function(*args, **kwargs)
    return decorator


def get_board():
    return {
        POSITION_BOSS: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_BOSS])).first(),
        POSITION_VICE: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_VICE])).first(),
        POSITION_TREASURE: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_TREASURE])).first(),
        POSITION_SECRET: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_SECRET])).first(),
        POSITION_LIBRARY: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_LIBRARY])).first(),
        POSITION_FREE: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_FREE])).all(),
        POSITION_COVISION: Fellow.query.filter(Fellow.board.op('&')(board_flags[POSITION_COVISION])).all(),
    }


def clear_board():
    for position_flag in POSITIONS_ALL:
        for fellow in Fellow.query.filter(Fellow.board.op('&')(board_flags[position_flag])).all():
            fellow.set_board(position_flag, False)

    db.session.commit()
