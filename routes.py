import os
import uuid
from flask import request, session, jsonify, redirect, render_template
from flask import current_app as app


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
        return render_template('home_auth.html', username=session['username'])
    else:
        return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login
    """
    if request.method == 'POST':
        # TODO: authentication
        session['username'] = request.form['username']
        return redirect('/')
    else:
        if 'username' in session:
            return redirect('/')
        else:
            return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    """Logout
    """
    session.pop('username', None)
    return redirect('/')
