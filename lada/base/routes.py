from flask import render_template
from datetime import date
from lada.base import bp
from lada.models import Fellow, brdfg 

@bp.route('/')
def index():
  return render_template('base/index.html', kmsage=int((date.today()-date(1893,12,3)).days/365.24))

def get_board():
  return {
      'prezes':Fellow.query.filter(Fellow.board.op('&')(brdfg['president']) == brdfg['president']).first(),
      'vice':Fellow.query.filter(Fellow.board.op('&')(brdfg['vice']) == brdfg['vice']).first(),
      'skarbnik':Fellow.query.filter(Fellow.board.op('&')(brdfg['treasurer']) == brdfg['treasurer']).first(),
      'sekretarz':Fellow.query.filter(Fellow.board.op('&')(brdfg['secretary']) == brdfg['secretary']).first(),
      'bibliotekarz':Fellow.query.filter(Fellow.board.op('&')(brdfg['librarian']) == brdfg['librarian']).first(),
      'wolny':Fellow.query.filter(Fellow.board.op('&')(brdfg['board']) == brdfg['board']).all(),
      'komisja':Fellow.query.filter(Fellow.board.op('&')(brdfg['revision']) == brdfg['revision']).all(),}

@bp.route('/board')
def board():
  return render_template('base/board.html', board=get_board())

@bp.route('/contact')
def contact():
  return render_template('base/contact.html')

@bp.route('/history')
def history():
  return render_template('base/history.html')
