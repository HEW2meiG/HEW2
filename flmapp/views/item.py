import os
from datetime import datetime
from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash, session
)
from flask_login import (
    login_user, login_required, current_user
)
from flmapp import db # SQLAlchemy

from flmapp.models.user import (
    User
)
from flmapp.models.trade import (
    Sell
)
from flmapp.forms.sell import (
    SellUpdateFlgAndDeleteForm
)

bp = Blueprint('item', __name__, url_prefix='/item')


@bp.route('/itemdata/<int:item_id>', methods=['GET', 'POST'])
def itemdata(item_id):
    # セッションの破棄
    session.pop('pay_way', None)
    session.pop('Credit_id', None)
    session.pop('ShippingAddress_id', None)
    item = Sell.query.get(item_id)
    form = SellUpdateFlgAndDeleteForm(request.form)
    return render_template('item/itemdata.html', item=item, form=form)