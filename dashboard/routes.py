import os

from flask import current_app as app
from flask import render_template, request
from trello import TrelloClient

from flask_login import login_user, logout_user, login_required, LoginManager

from flask import redirect
from flask import flash


from .data import DashboardData
from .models import User

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_SECRET = os.getenv('TRELLO_API_SECRET')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')



@app.login_manager.user_loader
def load_user(user_id: str):
    return User(user_id)

@app.route('/', methods=('GET',))
@login_required
def in_progress():
    dd = _load_data()
    in_progress_cards = dd.in_progress_cards()
    return render_template('in_progress.html', cards=in_progress_cards, title='In Progress Tasks')


@app.route('/done', methods=('GET',))
@login_required
def done():
    dd = _load_data()
    done_cards = dd.done_cards()
    return render_template('done.html', cards=done_cards, title='Completed Cards')


@app.route('/soon', methods=('GET',))
@login_required
def soon():
    dd = _load_data()
    soon_cards = dd.coming_soon_cards()
    return render_template('soon.html', cards=soon_cards, title='Cards Due Soon')


@app.route('/blocked', methods=('GET',))
@login_required
def blocked():
    dd = _load_data()
    blocked_cards = dd.blocked_cards()
    return render_template('in_progress.html', cards=blocked_cards, title='Blocked or Waiting Cards')


@app.route('/in-progress-activity', methods=('GET', ))
@login_required
def in_progress_activity():
    dd = _load_data()
    cards_by_label = dd.in_progress_activities()
    return render_template('activity.html', cards=cards_by_label, title='In Progress by Activity')


@app.route('/in-progress-products', methods=('GET', ))
@login_required
@login_required
def in_progress_products():
    dd = _load_data()
    cards_by_label = dd.in_progress_products()
    return render_template('products.html', cards=cards_by_label, title='In Progress by Product')


@app.route('/in-progress-epics', methods=('GET',))
@login_required
def in_progress_epics():
    dd = _load_data()
    cards_by_epic = dd.in_progress_epics()
    return render_template('epics.html', cards=cards_by_epic, title='In Progress by Epic')


@app.route('/in-progress-team', methods=('GET', ))
@login_required
def in_progress_team():
    dd = _load_data()
    cards_by_member = dd.in_progress_team()
    return render_template('team.html', cards=cards_by_member, title='In Progress by Team Member')


@app.route('/backlog', methods=('GET',))
@login_required
def backlog():
    dd = _load_data()
    backlog_cards = dd.backlog_cards()
    return render_template('in_progress.html', cards=backlog_cards, title='Tasks Backlog')


@app.route('/backlog-activity', methods=('GET', ))
@login_required
def backlog_activity():
    dd = _load_data()
    cards_by_label = dd.backlog_activities()
    return render_template('activity.html', cards=cards_by_label, title='Tasks Backlog by Activity')


@app.route('/backlog-products', methods=('GET', ))
@login_required
def backlog_products():
    dd = _load_data()
    cards_by_label = dd.backlog_products()
    return render_template('products.html', cards=cards_by_label, title='Tasks Backlog by Product')


@app.route('/backlog-epics', methods=('GET',))
@login_required
def backlog_epics():
    dd = _load_data()
    cards_by_epic = dd.backlog_epics()
    return render_template('epics.html', cards=cards_by_epic, title='Tasks Backlog by Epic')


@app.route('/backlog-team', methods=('GET', ))
@login_required
@login_required
def backlog_team():
    dd = _load_data()
    cards_by_member = dd.backlog_team()
    return render_template('team.html', cards=cards_by_member, title='Tasks Backlog by Team Member')


@app.route('/upcoming-events', methods=('GET', ))
@login_required
def upcoming_events():
    dd = _load_data()
    cards = dd.upcoming_events_cards()
    return render_template('events.html', cards=cards, title='Scheduled Events')


@app.route('/all-attendees', methods=('GET', ))
@login_required
def attendees():
    dd = _load_data()
    month_cards, month_data = dd.all_attendees()
    return render_template('attendees.html', cards=month_cards, data=month_data, title='Past Event Attendance')


@app.route('/customer-engagements', methods=('GET', ))
@login_required
def customer_engagements():
    dd = _load_data()
    month_cards, month_data = dd.customer_attendees()
    return render_template('attendees.html', cards=month_cards, data=month_data, title='Past Customer Engagement Attendance')


@app.route('/month', methods=('GET',))
@login_required
def month():
    dd = _load_data()

    month_list_id = request.args.get('month', None)
    if month_list_id:
        cards, list_name, stats = dd.month_highlights(month_list_id)
        if request.args.get('text', None):
            return render_template('highlights_text.html', cards=cards)
        else:
            return render_template('highlights.html', cards=cards, list_id=month_list_id, title=list_name, stats=stats)
    else:
        month_list = dd.month_list()
        return render_template('month_list.html', months=month_list, title='Monthly Highlights')

@app.route('/login', methods=["GET"])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    try:
        email = request.form.get("email")
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if email != app.config['ADMIN_USER'] or password != app.config['ADMIN_PASS']:
            flash('Please check your login details and try again')
            print('Invalid login attempt for admin: {}', email)
            return redirect("/login") # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        user = User(email)
        login_user(user, remember=remember)
        return redirect("/")
    except Exception as e:
        print("Couldn't login admin: {}", email)
        print(e)
    return redirect("/")

def _load_data() -> DashboardData:
    client = TrelloClient(api_key=TRELLO_API_KEY, api_secret=TRELLO_API_SECRET, token=TRELLO_TOKEN)
    dd = DashboardData()
    dd.load(client)

    return dd
