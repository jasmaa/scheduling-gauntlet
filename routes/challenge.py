from flask import request, session, redirect, render_template
from flask import current_app as app
from challenge import Problem, SchedulingMethod, Solver


@app.route('/challenge', methods=['POST', 'GET'])
def challenge():
    """Request and submit challenges
    """
    # Reject if not authenticated
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'GET':
        # Request challenge
        problem = Problem.generate(SchedulingMethod.FCFS, n_processes=3)
        session['problem'] = problem.to_json()
        return render_template('challenge.html', problem=problem)
    else:
        # Submit challenge
        problem = Problem.from_json(session['problem'])
        solver = Solver(problem)
        ans = solver.solve()
        print(ans)
        return render_template('challenge.html', problem=problem)
