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
    Project,
    Account,
)

home_page = Blueprint('home', __name__, template_folder="templates")
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


@home_page.route('/')
@home_page.route('/index')
def index():
    data = {'title': "New Donate.  Like Old Donate.  Only New."}
    return render_template('base.html',
                           title="New Donate",
                           data=data)


@projects_page.route('/projects')
def projects():
    projects = db.session.query(Project)
    return (render_template('projects.html',
                            title='Projects',
                            projects=projects))


@project_page.route('/projects/<project_name>')
def get_project(project_name):
    project = db.session.query(Project).filter_by(name == project_name)
    if len(project) == 0:
        redirect(url_for('new_project', project_name=project_name))
    if len(project) == 1:
        return (render_template('project.html',
                                title=project_name,
                                project=project))
    if len(project) > 1:
        raise ValueError("shit we're fucked in projects m8y!")


@new_project_page.route('/new/project/<project_name>')
def new_project(project_name, methods=['GET', 'POST']):
    name = project_name
    if request.method == "POST":
        goal = request.form['goal']
        ccy = request.form['ccy']
    pass


@new_account_page.route('/new/account')
def new_account():
    pass
