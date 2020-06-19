import sqlite3
from flask import (
    Blueprint,
    request,
    session,
    jsonify,
)
from flask.views import MethodView
from database import db

bp = Blueprint('users', __name__)


class UsersView(MethodView):
    def post(self):
        request_json = request.json
        email = request_json.get('email')
        password = request_json.get('password')
        first_name = request_json.get('first_name')
        last_name = request_json.get('last_name')
        is_seller = request_json.get('is_seller')
        phone = request_json.get('phone')
        zip_code = request_json.get('zip_code')
        # city_id = request_json.get('city_id')
        street = request_json.get('street')
        home = request_json.get('home')

        if not email or not password:
            return '', 400

        con = db.connection
        try:
            con.execute(
                'INSERT INTO account (email, password, first_name, last_name, is_seller) '
                'VALUES (?, ?, ?, ?, ?)',
                (email, password, first_name, last_name, is_seller),
            )
            con.commit()
            if is_seller:
                cur = con.execute(
                    'SELECT id '
                    'FROM account '
                    'WHERE email = ?',
                    (email,),
                )
                account_id = cur.fetchone()[0]
                print(account_id)
                con.execute(
                    'INSERT INTO seller (zip_code, street, home, phone, account_id) '
                    'VALUES (?, ?, ?, ?, ?)',
                    (zip_code, street, home, phone, account_id),
                )
            con.commit()
        except sqlite3.IntegrityError:
            return '', 409
        return '', 201


class UserView(MethodView):
    def get(self, user_id):

        con = db.connection
        cur = con.execute(
            'SELECT id, email '
            'FROM account '
            'WHERE id = ?',
            (user_id,),
        )
        user = cur.fetchone()
        if user is None:
            return '', 404
        if session['user_id'] == user['id']:
            # return 'sa', 200

            con = db.connection
            cur = con.execute(
                'SELECT is_seller '
                'FROM account '
                'WHERE id = ?',
                (user_id,),
            )
            seller_bool = int(cur.fetchone()[0])
            if not seller_bool:
                cur = con.execute(
                    'SELECT id, first_name, last_name, email, is_seller '
                    'FROM account '
                    'WHERE id = ?',
                    (user_id,),
                )
            else:
                cur = con.execute(
                    'SELECT account.id, email, first_name, last_name, is_seller, phone, street, home, zip_code, ('
                    'SELECT city_id FROM seller JOIN zipcode ON seller.zip_code=zipcode.zip_code) as city_id '
                    'FROM account JOIN seller ON account.id=seller.account_id '
                    'WHERE account.id = ?',
                    (user_id,),
                )
            user = cur.fetchone()
            if user is None:
                return '', 404
            return jsonify(dict(user, is_seller=bool(int(user['is_seller']))))

    def patch(self, user_id):
        request_json = request.json
        first_name = request_json.get('first_name')
        last_name = request_json.get('last_name')
        is_seller = request_json.get('is_seller')
        phone = request_json.get('phone')
        zip_code = request_json.get('zip_code')
        city_id = request_json.get('city_id')
        street = request_json.get('street')
        home = request_json.get('home')

        con = db.connection
        cur = con.execute(
            'SELECT id, email '
            'FROM account '
            'WHERE id = ?',
            (user_id,),
        )
        user = cur.fetchone()
        if user is None:
            return '', 404
        if session['user_id'] == user['id']:
            return '', 200
        con.execute(
            'UPDATE account '
            'SET first_name = ? '
            'WHERE id = ?',
            (first_name, user_id)
        )
        con.commit()
        return '', 200


bp.add_url_rule('', view_func=UsersView.as_view('users'))
bp.add_url_rule('/<int:user_id>', view_func=UserView.as_view('user'))
