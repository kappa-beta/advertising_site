from flask import (
    Blueprint,
    request,
    session,
    jsonify,
)
from flask.views import MethodView
from database import db

bp = Blueprint('ads', __name__)


class AdsView(MethodView):
    def get(self):
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM ad'
        )
        result = cur.fetchall()
        return jsonify([dict(row) for row in result])

    def post(self):
        user_id = session.get('user_id')
        if user_id is None:
            return '', 403

        request_json = request.json
        title = request_json.get('title')
        if not title:
            return '', 400

        con = db.connection
        con.execute(
            'INSERT INTO ad (title, user_id) '
            'VALUES (?, ?)',
            (title, user_id),
        )
        con.commit()

        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE user_id = ? AND title = ?',
            (user_id, title),
        )
        ad = cur.fetchone()
        return jsonify(dict(ad)), 201


class AdView(MethodView):
    def get(self, ad_id):
        con = db.connection
        cur = con.execute(
            'SELECT * '
            'FROM ad '
            'WHERE id = ?',
            (ad_id,),
        )
        ad = cur.fetchone()
        if ad is None:
            return '', 404
        return jsonify(dict(ad))


bp.add_url_rule('', view_func=AdsView.as_view('ads'))
bp.add_url_rule('/<int:ad_id>', view_func=AdView.as_view('ad'))