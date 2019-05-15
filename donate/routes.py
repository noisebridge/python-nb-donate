import git
import json
from flask import (
    render_template,
    flash,
    redirect,
    request,
    url_for,
    Blueprint,
)
from donate.database import db
from donate.models import (
    Account,
    Donation,
    Project,
)
import donate.widgets.stripe

import stripe
from donate.donations import _get_stripe_key
stripe.key = _get_stripe_key('SECRET')


donation_page = Blueprint('donation', __name__, template_folder="templates")
home_page = Blueprint('home', __name__, template_folder="templates")
thanks_page = Blueprint('thanks', __name__, template_folder="templates")
projects_page = Blueprint('projects', __name__, template_folder="templates")
project_page = Blueprint('project', __name__, template_folder="templates")
new_project_page = Blueprint(
    'new_project',
    __name__,
    template_folder="templates")
new_account_page = Blueprint(
    'new_account',
    __name__,
    template_folder="templates")
git_sha = git.Repo(search_parent_directories=True).head.object.hexsha
repo_path = "https://github.com/marcidy/nb_donate/commits/"
donation_charges = Blueprint(
    'new_charge',
    __name__,
    template_folder="templates")


def write_donation_to_db(full, params, stripe_donation):
    """Note: stripe_donation can be the id of a charge or a subscription
    depending on params['recurring']
    """
    print(stripe_donation)
    print(params)
    return "@TODO: implement write_donation_to_db"


def get_donation_params(form):
    try:
        charges = list(map(int,
                           filter(lambda a: a != "" and a != "other",
                                  form.getlist('charge[amount]'))))
        return (None, {
            'charge': charges[0],
            'email': form['donor[email]'],
            'name': form['donor[name]'],
            'stripe_token': form['donor[stripe_token]'],
            'recurring': 'charge[recurring]' in form,
            'anonymous': 'donor[anonymous]' in form
        })
    except KeyError as e:
        return ("Error: required form value %s not set." % e.args[0], None)
    except ValueError as e:
        return ("Error: please enter a valid amount for your donation", None)


def charge_amount_as_cents(dollars):
    return int(dollars*100)


def flash_donation_err(err):
    flash(err)
    return redirect('/index#form')


@donation_page.route('/donation', methods=['POST'])
def donation():
    full = request.get_data()

    (err, params) = get_donation_params(request.form)
    if err:
        return flash_donation_err(err)

    cents = charge_amount_as_cents(params['charge'])
    (err, charge_id) = donate.widgets.stripe.create_charge(
        params['recurring'], params['stripe_token'], cents, params['email'])
    if err:
        return flash_donation_err(err)

    err = write_donation_to_db(full, params, charge_id)
    if err:
        return flash_donation_err(err)

    return redirect('/thanks')


@home_page.route('/')
@home_page.route('/index')
def index():
    """ setup main page with overview of projects, recent donations, and
    other summary data
    """

    sorted_projects = sorted(db.session.query(Project).all(),
                             key=lambda proj: proj.name)

    donations = db.session.query(Donation).limit(10)

    return render_template('main.html',
                           data={
                               'git_sha': git_sha,
                               'repo_path': repo_path,
                               'recent_donations': donations,
                               'projects': sorted_projects,
                               'stripe_pk': db.get_app().config['STRIPE_PK']
                           })


@thanks_page.route('/thanks')
def thanks():
    """ A quick thank you shown after a person donates. """
    return render_template('thanks.html',
                           data={
                               'git_sha': git_sha,
                               'repo_path': repo_path
                           })


@projects_page.route('/projects')
def projects():
    """ Return a list of projects, sorted by project name """
    projects = sorted(db.session.query(Project).all(),
                      key=lambda proj: proj.name)

    return render_template('projects.html',
                           title='Projects',
                           projects=sorted_projects)


@project_page.route('/projects/<project_name>')
def get_project(project_name):
    """ Return a project indicated by the direcdt link. If it doesn't exist,
    return the new project page.
    """
    project = db.session.query(Project).filter_by(name == project_name)
    if len(project) == 0:
        return new_project(project_name)
    if len(project) == 1:
        return (render_template('project.html',
                                title=project_name,
                                project=project[0]))
    if len(project) > 1:
        raise ValueError("Critical Error: Projects exist with identical name")


@new_project_page.route('/new/project/<project_name>', methods=['GET', 'POST'])
def new_project(project_name):
    """ Return a page to create a new project """
    if request.method == "POST":
        goal = request.form['goal']
        ccy_code = request.form['ccy']
        desc = request.form['desc']

        acct = Account(name="{}_{}_acct".format(project_name, ccy_code),
                       ccy=db.session.query('Currency').
                       filter(code=ccy_code).one())

        project = Project(name=project_name,
                          desc=desc,
                          goal=goal,
                          accounts=[acct])

        db.session.add(project)
        db.session.commit()

        # TODO: send the new project to the database
        return (render_template('new_project_created.html',
                                title=project_name,
                                project=project))
    else:
        return (render_template('new_project.html',
                                title=project_name,
                                project=project))


@new_account_page.route('/new/account')
def new_account():
    pass


@donation_charges.route('/donations/charges')
def new_charge():

    if request.method == 'POST':
        form = request.form

        return(redirect('thanks.html'))
    return(redirect('index'))
