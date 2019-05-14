import git
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
                               'projects': sorted_projects
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
