from flask import request, session, redirect, render_template
from flask import current_app as app


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
