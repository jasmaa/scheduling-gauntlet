from flask import session, render_template, redirect, flash
from flask import current_app as app
from flask.globals import request
from models import db, User
from utils import validate_email

# Import routes
from . import auth
from . import challenge


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


@app.route('/about', methods=['GET'])
def about():
    """About page
    """

    if 'username' in session:
        u = User.query.filter_by(username=session['username']).first()
        return render_template(
            'about.html',
            username=session['username'],
            score=u.score,

        )
    else:
        return render_template(
            'about.html',
        )


@app.route('/scoreboard', methods=['GET'])
def scoreboard():
    """Displays leaderboard
    """

    # Get top 20 users
    top_users = User.query.order_by(User.score.desc()).limit(20).all()
    top_users = [{
        'username': u.username,
        'score': u.score,
    } for u in top_users]

    if 'username' in session:
        u = User.query.filter_by(username=session['username']).first()
        return render_template(
            'scoreboard.html',
            username=session['username'],
            score=u.score,
            top_users=top_users,
        )
    else:
        return render_template(
            'scoreboard.html',
            top_users=top_users,
        )


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """Edit profile information
    """

    if 'username' not in session:
        return redirect('/')

    u = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        if username == None or len(username) == 0:
            # No username
            flash('Username is required.', 'error')
            return render_template('edit_profile.html')

        if email == None or len(email) == 0:
            # No email
            flash('Email is required.', 'error')
            return render_template('edit_profile.html')

        if not validate_email(email):
            # Email is invalid
            flash('Email is invalid.', 'error')
            return render_template('edit_profile.html')

        other_u = User.query.filter_by(username=username).first()
        if other_u != None and other_u != u:
            # Username already taken
            flash('Username is already taken.', 'error')
            return render_template('edit_profile.html')

        other_u = User.query.filter_by(email=email).first()
        if other_u != None and other_u != u:
            # Email already taken
            flash('Email is already taken.', 'error')
            return render_template('edit_profile.html')

        # Update profile
        u.username = username
        u.email = email
        db.session.commit()

        # Update session
        session['username'] = username

        flash('Profile successfully updated!', 'info')
        return render_template(
            'edit_profile.html',
            username=u.username,
            email=u.email,
            score=u.score,
        )

    else:
        return render_template(
            'edit_profile.html',
            username=u.username,
            email=u.email,
            score=u.score,
        )


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """Change password
    """

    if 'username' not in session:
        return redirect('/')

    u = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        old_password = request.form['old-password']
        password = request.form['password']
        password_check = request.form['password-check']

        if not u.validate(old_password):
            # Invalid password
            flash('Old password was incorrect.', 'error')
            return render_template('change_password.html')

        if password == None or len(password) == 0:
            # No password
            flash('Password is required.', 'error')
            return render_template('change_password.html')

        if password != password_check:
            # Passwords do not match
            flash('Passwords do not match.', 'error')
            return render_template('change_password.html')

        # Update profile
        u.set_password(password)
        db.session.commit()

        flash('Password successfully updated!', 'info')
        return render_template('change_password.html', username=u.username, score=u.score)

    else:
        return render_template('change_password.html', username=u.username, score=u.score)
