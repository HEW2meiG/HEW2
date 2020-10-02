from flask import (
     Blueprint, abort, request, render_template,
    redirect, url_for, flash
)

bp = Blueprint('route', __name__, url_prefix='')

@bp.route('/')
def home():
    return render_template('home.html')

# ページが見つからない場合
@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('route.home'))

@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500