from flask import request, session, redirect, render_template
from flask import current_app as app
from challenge import Problem, SchedulingMethod, Solver
from utils import parse_int


@app.route('/challenge', methods=['POST', 'GET'])
def challenge():
    """Request and submit challenges
    """
    # Reject if not authenticated
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'GET':
        # Display challenge
        # Request challenge if no current problem
        if session['problem'] == None:
            problem = Problem.generate(SchedulingMethod.FCFS, n_processes=3)
            session['problem'] = problem.to_json()
        else:
            problem = Problem.from_json(session['problem'])

        return render_template('challenge.html', problem=problem)

    else:
        # Submit challenge
        # Request new problem if no current problem
        if session['problem'] == None:
            return redirect('/challenge')

        problem = Problem.from_json(session['problem'])

        # Solve problem
        solver = Solver(problem)
        ans = solver.solve()

        # Parse and validate input
        is_correct = True
        for i, (finish_t, wait_t) in enumerate(ans):
            finish_t_guess = parse_int(request.form[f'finish_{i}'])
            if finish_t_guess != finish_t:
                is_correct = False
                break

            wait_t_guess = parse_int(request.form[f'wait_{i}'])
            if wait_t_guess != wait_t:
                is_correct = False
                break

        # Reset problem
        session['problem'] = None

        return render_template(
            'challenge_done.html',
            problem=problem,
            is_correct=is_correct,
            answer_times=ans,
        )
