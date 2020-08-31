import functools
from flask_login import current_user

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
      if current_user.check_board('boss') or current_user.check_board('vice') or any(current_user.check_board(pos) for pos in position): 
        value = function(*args, **kwargs)
        return value
      else:
        flash('You do not have acess to this site.')
        return redirect(url_for('base.index'))
    return wrapper
  return decorator
