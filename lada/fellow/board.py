import functools

from flask import flash, redirect, url_for
from flask_login import current_user

from lada.models import Fellow, brdfg

position = {
    'boss':'Prezes',
    'vice':'Wiceprezes',
    'treasure':'Skarbnik',
    'secret':'Sekretarz',
    'library':'Bibiotekarz',
    'free':'Wolny Członek',
    'covision':'Komisja Rewizyjna',
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
      'boss':Fellow.query.filter(Fellow.board.op('&')(brdfg['boss']) == brdfg['boss']).first(),
      'vice':Fellow.query.filter(Fellow.board.op('&')(brdfg['vice']) == brdfg['vice']).first(),
      'treasure':Fellow.query.filter(Fellow.board.op('&')(brdfg['treasure']) == brdfg['treasure']).first(),
      'secret':Fellow.query.filter(Fellow.board.op('&')(brdfg['secret']) == brdfg['secret']).first(),
      'library':Fellow.query.filter(Fellow.board.op('&')(brdfg['library']) == brdfg['library']).first(),
      'free':Fellow.query.filter(Fellow.board.op('&')(brdfg['free']) == brdfg['free']).all(),
      'covision':Fellow.query.filter(Fellow.board.op('&')(brdfg['covision']) == brdfg['covision']).all(),}
