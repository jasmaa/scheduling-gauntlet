from flask import request, session, jsonify, redirect, render_template
from flask import current_app as app
from models import db, User
from . import auth
from . import challenge


@app.route('/dummy', methods=['GET'])
def dummy():
    """Dummy handler
    """
    return jsonify('dummy'), 200


@app.route('/', methods=['GET'])
def home():
    """Home page
    """
    if 'username' in session:
        u = User.query.filter_by(username=session['username']).first()
        return render_template(
            'home_auth.html',
            username=session['username'],
            score=u.score,
        )
    else:
        return render_template('home.html')
