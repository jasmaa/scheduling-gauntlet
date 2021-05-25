from flask import request, session, redirect, render_template, flash
from flask import current_app as app
from models import db, User
from mailer import send
from utils import validate_email, generate_code


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """Sign up
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_check = request.form['password-check']

        if username == None or len(username) == 0:
            # No username
            flash('Username is required.', 'error')
            return render_template('signup.html')

        if email == None or len(email) == 0:
            # No email
            flash('Email is required.', 'error')
            return render_template('signup.html')

        if password == None or len(password) == 0:
            # No password
            flash('Password is required.', 'error')
            return render_template('signup.html')

        if not validate_email(email):
            # Email is invalid
            flash('Email is invalid.', 'error')
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

        u = User.query.filter_by(email=email).first()
        if u != None:
            # Email already taken
            flash('Email is already taken.', 'error')
            return render_template('signup.html')

        try:
            u = User.create_user(
                username=username, email=email, password=password)
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
            u = User.query.filter_by(email=username).first()
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


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    """Password reset request
    """
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        u = User.query.filter_by(username=username).first()
        if u == None:
            u = User.query.filter_by(email=username).first()
            if u == None:
                # No user found
                flash('No user found under that username/email.', 'error')
                return render_template('password_reset_request.html')

        # Generate and set code for user
        code = generate_code()
        u.code = code
        db.session.commit()

        # Send email with reset link
        callback_url = f'{request.base_url}/callback?code={code}&email={u.email}'
        send(
            to=u.email,
            subject='Password Reset was Requested',
            body=f'Password request link: {callback_url}',
        )

        flash('Email requesting password reset successfully sent!', 'info')
        return render_template('password_reset_request.html')

    else:
        return render_template('password_reset_request.html')


@app.route('/password_reset/callback', methods=['GET', 'POST'])
def password_reset_callback():
    """Password reset callback
    """
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        code = request.form['code']
        email = request.form['email']
        password = request.form['password']
        password_check = request.form['password-check']

        if email == None:
            return redirect('/')
        if code == None:
            return redirect('/')

        u = User.query.filter_by(email=email).first()
        if code != u.code:
            # Invalid code
            return redirect('/')

        if password == None or len(password) == 0:
            # No password
            flash('Password is required.', 'error')
            return render_template('password_reset.html', email=email, code=code)

        if password != password_check:
            # Passwords do not match
            flash('Passwords do not match.', 'error')
            return render_template('password_reset.html', email=email, code=code)

        # Update password and code
        u.set_password(password)
        u.code = None
        db.session.commit()

        flash('Password successfully reset!', 'info')
        return render_template('password_reset.html')

    else:
        code = request.args.get('code')
        email = request.args.get('email')

        if code == None:
            return redirect('/')
        if email == None:
            return redirect('/')

        u = User.query.filter_by(email=email).first()
        if u.code != code:
            # Invalid code
            return redirect('/')

        return render_template('password_reset.html', email=email, code=code)


@app.route('/logout', methods=['POST'])
def logout():
    """Logout
    """
    session.pop('username', None)
    return redirect('/')
