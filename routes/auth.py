import psycopg2
from flask import request, session, redirect, render_template, flash
from flask import current_app as app
import sqlalchemy
from models import db, User


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """Sign up
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_check = request.form['password-check']

        if username == None or len(username) == 0:
            flash('Username is required.', 'error')
            return render_template('signup.html')

        if password == None or len(password) == 0:
            flash('Password is required.', 'error')
            return render_template('signup.html')

        if password != password_check:
            # Passwords do not match
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        u = User.query.filter_by(username=username).first()
        if u != None:
            # Username already taken
            flash('Username is already taken.', 'error')
            return render_template('signup.html')

        try:
            u = User.create_user(username=username, password=password)
            db.session.add(u)
            db.session.commit()
        except:
            flash('Error occured during sign up.', 'error')
            return render_template('signup.html')

        flash('Successfully signed up!', 'info')
        return render_template('signup.html')

    else:
        if 'username' in session:
            return redirect('/')
        else:
            return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        u = User.query.filter_by(username=username).first()
        if u == None:
            # No user found
            flash('Username or password was incorrect.', 'error')
            return render_template('login.html')

        if not u.validate(password):
            # Invalid password
            flash('Username or password was incorrect.', 'error')
            return render_template('login.html')

        # Log user in
        session['username'] = u.username
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
