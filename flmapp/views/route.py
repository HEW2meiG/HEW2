from flask import (
     Blueprint, abort, request, render_template,
    redirect, url_for, flash
)

from flmapp.models.user import (
    User
)
from flmapp.models.trade import (
    Sell
)
from flmapp.models.reaction import (
    Likes, UserConnect
)
from flmapp.models.message import(
    PostMessage, DealMessage
)

bp = Blueprint('route', __name__, url_prefix='')

# ホーム
@bp.route('/')
def home():
    items = Sell.query.all()
    return render_template('home.html', items=items)

# ページが見つからない場合
@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect(url_for('route.home'))

@bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500