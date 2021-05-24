from flask import session, render_template
from flask import current_app as app
from models import User

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
