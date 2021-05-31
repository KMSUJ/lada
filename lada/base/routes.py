from datetime import date

from flask import render_template, url_for, redirect, request

from lada.base import bp


@bp.route('/')
def index():
    return render_template('base/index.html', kmsage=int((date.today() - date(1893, 12, 3)).days / 365.24))


@bp.route('/board')
def board():
    return render_template('base/board.html')


@bp.route('/contact')
def contact():
    return render_template('base/contact.html')


@bp.route('/history')
def history():
    return render_template('base/history.html')


@bp.route('/fix', methods=['GET'])
def fix():
    response = redirect(url_for("base.index"))
    for cookie in request.cookies.keys():
        response.delete_cookie(cookie)
    return response
