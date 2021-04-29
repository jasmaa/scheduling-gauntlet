from flask import request, session, redirect, render_template
from flask import current_app as app


@app.route('/challenge', methods=['POST', 'GET'])
def challenge():
    """Request and submit challenges
    """
    # Reject if not authenticated
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'GET':
        # Request challenge
        pass
    else:
        # Submit challenge
        pass
