from flask import (
    Blueprint,
    request,
    session,
)
from database import db

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    request_json = request.json
    email = request_json.get('email')
    password = request_json.get('password')

    if not email or not password:
        return '', 400

    con = db.connection
    cur = con.execute(
        'SELECT * '
        'FROM account '
        'WHERE email = ?',
        (email,),
    )
    user = cur.fetchone()

    if user is None:
        return '', 403

    # password_hash = md5(password.encode() + app.secret_key).hexdigest()
    if user['password'] != password:
        return '', 403

    session['user_id'] = user['id']
    return f'Авторизация пользователя: {user["id"]}', 200


@bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return '', 200
