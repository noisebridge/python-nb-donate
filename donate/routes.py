from flask import (
    current_app as app,
    flash,
    redirect,
    render_template,
    request,
    Blueprint,
)
from sqlalchemy.orm.exc import (
    NoResultFound,
)
from donate.util import (
    get_one,
    obtain_model,
)
from donate.extensions import db
from donate.models import (
    Account,
    Project,
    Currency,
    Transaction,
    StripeDonation,
    StripePlan,
    StripeSubscription,
)
from donate.vendor.stripe import (
    PaymentFlowError,
    StripeAPICallError,
    flow_stripe_payment
)

# FIXME: git_sha = git.Repo(search_parent_directories=True).head.object.hexsha
git_sha = "whatever"
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


class DonationFormError(Exception):
    pass


def get_donation_params(form):
    try:
        charges = [charge for charge
                   in form.getlist('charge[amount]')
                   if charge not in ["", "other", ' ']]
        if form['donor[email]'] == '':
            raise KeyError('email')
        ret = {
            'charge': charges[0],
            'email': form['donor[email]'],
            'name': form.get('donor[name]', "Anonymous"),
            'stripe_token': form['donor[stripe_token]'],
            'recurring': 'charge[recurring]' in form,
            'anonymous': 'donor[anonymous]' in form,
            'project_select': form['project_select']}

    except KeyError as e:
        err_msg = e.args[0]
        app.logger.debug("Params not set: {}".format(err_msg))
        raised_msg = "Error: required form value {} not set.".format(err_msg)
        raise DonationFormError(raised_msg)
    except IndexError as e:
        err_msg = e.args[0]
        app.logger.debug("Params bad Value: {}".format(err_msg))
        raised_msg = "Error: please enter a valid amount for your donation"
        raise DonationFormError(raised_msg)
    return ret


def model_stripe_data(stripe_data, params):
    app.logger.info("Modelling stripe data")

    customer = stripe_data['customer']
    email = customer.email
    from_acc_name = email

    if 'charge' in stripe_data:
        charge = stripe_data['charge']
        amount = charge.amount
        ccy = charge.currency.upper()

    if 'subscription' in stripe_data:
        subscription = stripe_data['subscription']
        plan = subscription.plan
        amount = plan.amount
        ccy = plan.currency.upper()

    if (app.config['SINGLE_CCY'] and ccy != "USD"):
        raise ValueError("Attempt to create non-USD donation!")

    # These will raise errors if not found or more than one found.  They
    # should bubble up to the route.
    ccy = get_one(Currency, {'code': ccy})

    from_acct = obtain_model(Account, {'name': from_acc_name, 'ccy': ccy},
                             {'name': from_acc_name, 'ccy': ccy})

    # find the project receiving the donation and get it's account
    project = get_one(Project, {'name': stripe_data['project']})

    for project_account in project.accounts:
        if project_account.ccy.code == ccy.code:
            to_acct = project_account
        else:
            app.logger.error("No account with ccy {} "
                             "on project {}".format(ccy.code, project.name))
            raise NoResultFound

    if 'subscription' in stripe_data:
        app.logger.debug("Creating Subscription")
        stripe_sub = StripeSubscription(email=email, customer_id=customer.id)
        stripe_plan = obtain_model(StripePlan,
                                   gets={'name': plan.name},
                                   sets={'name': plan.name,
                                         'amount': amount,
                                         'interval': 'M',
                                         'desc': "${}/{}".format(amount/100,
                                                                 "M")})
        stripe_plan.subscriptions.append(stripe_sub)

        app.logger.debug("Adding Subscription to "
                         "plan {} for user {}"
                         .format(plan.name, email))
        from_acct.subscriptions.append(stripe_sub)
        return [stripe_plan, from_acct]

    else:
        app.logger.debug("Creating Transaction")
        # create transaction between the accounts
        tx = Transaction(amount=amount,
                         ccy=ccy,
                         payer=from_acct,
                         recvr=to_acct)

        dbg_msg = "Creating StripeDonation - "
        dbg_msg += "anon: {}, charge_id: {}, customer: {}"
        dbg_msg = dbg_msg.format(params['anonymous'], charge.id, customer.id)
        app.logger.debug(dbg_msg)

        sd = StripeDonation(
            anonymous=params['anonymous'],
            charge_id=charge.id,
            customer_id=customer.id)
        sd.txs = tx
    return [sd]


@donation_page.route('/donation', methods=['POST'])
def donation():
    """ Processes a stripe donation. """

    app.logger.debug("Entering route /donation")
    request_data = request.get_data()
    app.logger.debug("Request Data: {}".format(request_data))

    try:
        params = get_donation_params(request.form)
    except DonationFormError as e:
        flash(e.args[0])
        return redirect('/index#form')

    app.logger.debug("Params: {}".format(params))
    amount_in_cents = int(round(float(params['charge']), 2) * 100)
    app.logger.debug("Amount: {}".format(amount_in_cents))

    try:
        app.logger.debug("Flowing Stripe Payment -- email: {}, source: {}"
                         " amount_in_cents: {}, recurring: {}".format(
                             params['email'], params['stripe_token'],
                             amount_in_cents, params['recurring']))
        stripe_data = flow_stripe_payment(
            email=params['email'],
            source=params['stripe_token'],  # appended by donate.js
            amount_in_cents=amount_in_cents,
            recurring=params['recurring'])

    except PaymentFlowError as error:
        app.logger.error(error.args[0])
        flash("Unexpected error, please check data and try again."
              "  If the error persists, please contact Noisebridge support")
        return redirect('/index#form')
    except StripeAPICallError as error:
        app.logger.warning(error.log_msg)
        flash(error.user_msg)
        return redirect('/index#form')
        # TODO log request data, make sure charge failed

    # Add models to the DB
    stripe_data['project'] = params['project_select']
    models = model_stripe_data(stripe_data, params)
    try:
        for model in models:
            db.session.add(model)
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
        return new_project()
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
