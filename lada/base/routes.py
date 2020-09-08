from datetime import date

from flask import render_template

from lada.base import bp
from lada.fellow.board import get_board

@bp.route('/')
def index():
  return render_template('base/index.html', kmsage=int((date.today()-date(1893,12,3)).days/365.24))

@bp.route('/board')
def board():
  return render_template('base/board.html', board=get_board())

@bp.route('/contact')
def contact():
  return render_template('base/contact.html')

@bp.route('/history')
def history():
  return render_template('base/history.html')
