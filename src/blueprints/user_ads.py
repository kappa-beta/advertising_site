from flask import (
    Blueprint,
    request,
    session,
    jsonify,
)
from flask.views import MethodView
from database import db

bp = Blueprint('user_ads', __name__)


class UserAdsView(MethodView):
    def get(self, user_id):
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE user_id = ?',
            (user_id,),
        )
        result = cur.fetchall()
        return jsonify([dict(row) for row in result])


bp.add_url_rule('/<int:user_id>/ads', view_func=UserAdsView.as_view('user_ads'))
