import os
import git
import json
from flask import (
    current_app as app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    Blueprint,
)
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from donate.util import get_one
from donate.database import db
from donate.models import (
    Account,
    Donation,
    Project,
    Currency,
    Transaction,
    StripeDonation,
    StripePlan,
    StripeSubscription,
)
from donate.vendor.stripe import (
    create_charge,
    get_customer
)

import stripe
from stripe import error as se

git_sha = git.Repo(search_parent_directories=True).head.object.hexsha
repo_path = "https://github.com/noisebridge/python-nb-donate/tree/"

donation_page = Blueprint('donation', __name__, template_folder="templates")
home_page = Blueprint('home', __name__, template_folder="templates")
thanks_page = Blueprint('thanks', __name__, template_folder="templates")
projects_page = Blueprint('projects', __name__, template_folder="templates")
project_page = Blueprint('project', __name__, template_folder="templates")
new_project_page = Blueprint('new_project',
                             __name__, template_folder="templates")
new_account_page = Blueprint('new_account',
                             __name__, template_folder="templates")
donation_charges = Blueprint('new_charge',
                             __name__, template_folder="templates")


def get_donation_params(form):
    charges = [charge for charge
               in form.getlist('charge[amount]')
               if charge not in ["", "other", ' ']]
    ret = {
        'charge': charges[0],
        'email': form['donor[email]'],
        'name': form.get('donor[name]', "Anonymous"),
        'stripe_token': form['donor[stripe_token]'],
        'recurring': 'charge[recurring]' in form,
        'anonymous': 'donor[anonymous]' in form,
        'project_select': form['project_select']}
    return ret


def model_stripe_data(req_data):
    app.logger.info("Modelling stripe data")

    if app.config['SINGLE_CCY']:
        ccy_name = "USD"  # FIXME more generic...i mean..maybe

    to_proj = req_data['project_select']
    from_acc_name = req_data['email']
    amount = int(round(float(req_data['charge']), 2) * 100)

    # These will raise errors if not found or more than one found.  They
    # should bubble up to the route.
    project = get_one(Project, {'name': to_proj})
    ccy = get_one(Currency, {'code': ccy_name})

    # Check for user account (e.g. the account from which the spice will flow)
    app.logger.info("Finding account {}.".format(from_acc_name))
    try:
        from_acct = get_one(Account,
                            {'name': from_acc_name,
                             'ccy': ccy})
    # if it doesn't exist, make it.
    except NoResultFound:
        app.logger.info("Customer Account not found, creating account"
                        " for new customer {}".format(from_acc_name))
        from_acct = Account(name=from_acc_name,
                            ccy=ccy)

    for project_account in project.accounts:
        if project_account.ccy.code == ccy_name:
            to_acct = project_account

    try:
        to_acct
    except NameError:
        app.logger.error("No account with ccy {} "
                         "on project {}".format(ccy_name, to_proj))
        raise NoResultFound

    tx = Transaction(amount=amount,
                     ccy=ccy,
                     payer=from_acct,
                     recvr=to_acct)

    return tx


@donation_page.route('/donation', methods=['POST'])
def donation():
    """ Processes a stripe donation. """

    app.logger.debug("Entering route /donation")
    request_data = request.get_data()
    app.logger.debug("Request Data: {}".format(request_data))

    try:
        params = get_donation_params(request.form)
    except KeyError as e:
        app.logger.debug("Params not set: {}".format(e.args[0]))
        flash("Error: required form value %s not set." % e.args[0])
        return redirect('/index#form')
    except ValueError as e:
        app.logger.debug("Params bad Value: {}".format(e.args[0]))
        flash("Error: please enter a valid amount for your donation")
        return redirect('/index#form')

    app.logger.debug("Params: {}".format(params))
    amt = int(round(float(params['charge']), 2) * 100)
    app.logger.debug("Amount: {}".format(amt))

    try:
        charge_data = create_charge(
            params['recurring'],
            params['stripe_token'],  # appended by donate.js
            amt,
            params['email'])
        app.logger.debug("Charge created: {}".format(charge_data))

    except se.CardError as error:
        if error.json_body is not None:
            err = error.json_body.get('error', {})
            msg = err.get('message', "Unknown Card Error")
            app.logger.error("CardError: {}".format(err))
        else:
            msg = "Unknown Card Error"
            app.logger.error("CardError: {}".format(error))
        flash(msg)
        return redirect('/index#form')
    except se.RateLimitError as error:
        app.logger.warn("RateLimitError hit!")
        flash("Rate limit hit, please try again in a few seconds")
        return redirect('/index#form')
    except se.StripeError as error:
        app.logger.error("StripeError: {}".format(error))
        flash("Unexpected error, please check data and try again."
              "  If the error persists, please contact Noisebridge support")
        return redirect('/index#form')
        # TODO log request data, make sure charge failed

    if params['recurring']:
        app.logger.debug("Creating Subscription")

        stripe_sub = StripeSubscription(
            email=params['email'],
            customer_id=charge_data['customer_id'])

        plan_name = "{} / Month".format(amt)

        app.logger.debug("Checking for Stripe Plan {}".format(plan_name))
        try:
            stripe_plan = get_one(StripePlan, {'name': plan_name})
        except NoResultFound:
            app.logger.debug("Creating plan {}".format(plan_name))
            stripe_plan = StripePlan(name=plan_name,
                               amount=amt,
                               interval="M",
                               desc="{}/{}".format(amt, "M"))
            stripe_plan.subscriptions=[stripe_sub]
        try:
            stripe_plan
        except NameError:
            app.logging.error("Something went horribly wrong with StripePlan")

        app.logger.debug("Adding Subscription to "
                         "plan {} for user {}"
                         .format(plan_name, params['email']))
        stripe_plan.subscriptions.append(stripe_sub)

        try:
            db.session.add(stripe_plan)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    else:
        app.logger.debug("Creating Transaction")
        tx = model_stripe_data(req_data=params)

        app.logger.debug("Creating StripeDonation -  anon: {}, card_id: {}, "
                         "charge_id: {}, email: {}".format(params['anonymous'],
                                                params['stripe_token'],
                                                charge_data['charge_id'],
                                                charge_data['customer_id']))
        sd = StripeDonation(
            anonymous=params['anonymous'],
            card_id=params['stripe_token'],
            charge_id=charge_data['charge_id'],
            customer_id=charge_data['customer_id'])
        sd.txs = tx

        try:
            db.session.add(tx)
            db.session.add(sd)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    return redirect('/thanks')


@home_page.route('/')
@home_page.route('/index')
def index():
    """ setup main page with overview of projects, recent donations, and
    other summary data
    """

    sorted_projects = sorted(db.session.query(Project)
                             .filter(Project.name != "General Fund").all(),
                             key=lambda proj: proj.name)

    # donations = db.session.query(Donation).limit(10)
    donations = []
    STRIPE_KEY = app.get_stripe_key('PUBLIC')

    return render_template('main.html',
                           data={
                               'git_sha': git_sha,
                               'repo_path': repo_path,
                               'recent_donations': donations,
                               'projects': sorted_projects,
                               'stripe_pk': STRIPE_KEY
                           })


@thanks_page.route('/thanks')
def thanks():
    """ A quick thank you shown after a person donates. """
    data = {'git_sha': git_sha, 'repo_path': repo_path}
    return render_template('thanks.html', data=data)


@projects_page.route('/projects')
def projects():
    """ Return a list of projects, sorted by project name """
    projects = sorted(db.session.query(Project).all(),
                      key=lambda proj: proj.name)

    return render_template('projects.html',
                           title='Projects',
                           projects=projects)


@project_page.route('/projects/<project_name>')
def get_project(project_name):
    """ Return a project indicated by the direcdt link. If it doesn't exist,
    return the new project page.
    """
    project = db.session.query(Project).filter_by(name=project_name).all()
    if len(project) == 0:
        return new_project(project_name)
    if len(project) == 1:
        return (render_template('project.html',
                                title=project_name,
                                project=project[0]))
    if len(project) > 1:
        raise ValueError("Critical Error: Projects exist with identical name")


@new_project_page.route('/new/project', methods=['GET', 'POST'])
def new_project():
    """ Return a page to create a new project """

    if request.method == "POST":
        goal = int(request.form['goal'])
        ccy_code = request.form['ccy']
        desc = request.form['desc']
        project_name = request.form['project_name']

        ccy = db.session.query(Currency).filter_by(code=ccy_code).one()
        acct = Account(name="{}_{}_acct".format(project_name, ccy_code),
                       ccy=ccy)

        project = Project(name=project_name,
                          desc=desc,
                          goal=goal)
        project.accounts = [acct]

        db.session.add(project)
        db.session.commit()

        # TODO: send the new project to the database
        return (render_template('new_project_created.html',
                                title=project_name,
                                project=project))
    else:
        return render_template('new_project.html',
                               data={'git_sha': git_sha,
                                     'repo_path': repo_path})


@new_account_page.route('/new/account')
def new_account():
    pass
