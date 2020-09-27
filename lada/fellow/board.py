import functools

from flask import flash, redirect, url_for
from flask_login import current_user

from lada.models import Fellow, board_flags

position = {
    'boss': 'Prezes',
    'vice': 'Wiceprezes',
    'treasure': 'Skarbnik',
    'secret': 'Sekretarz',
    'library': 'Bibiotekarz',
    'free': 'Wolny Członek',
    'covision': 'Komisja Rewizyjna',
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
        'boss': Fellow.query.filter(Fellow.board.op('&')(board_flags['boss']) == board_flags['boss']).first(),
        'vice': Fellow.query.filter(Fellow.board.op('&')(board_flags['vice']) == board_flags['vice']).first(),
        'treasure': Fellow.query.filter(
            Fellow.board.op('&')(board_flags['treasure']) == board_flags['treasure']).first(),
        'secret': Fellow.query.filter(Fellow.board.op('&')(board_flags['secret']) == board_flags['secret']).first(),
        'library': Fellow.query.filter(Fellow.board.op('&')(board_flags['library']) == board_flags['library']).first(),
        'free': Fellow.query.filter(Fellow.board.op('&')(board_flags['free']) == board_flags['free']).all(),
        'covision': Fellow.query.filter(
            Fellow.board.op('&')(board_flags['covision']) == board_flags['covision']).all(), }


def clear_board():
    for fellow in Fellow.query.filter(Fellow.board.op('&')(board_flags['board']) == board_flags['board']).all():
        fellow.set_board('board', False)
        fellow.set_board('boss', False)
        fellow.set_board('vice', False)
        fellow.set_board('treasure', False)
        fellow.set_board('secret', False)
        fellow.set_board('library', False)
        fellow.set_board('free', False)

    for fellow in Fellow.query.filter(Fellow.board.op('&')(board_flags['covision']) == board_flags['covision']).all():
        fellow.set_board('covision', False)
