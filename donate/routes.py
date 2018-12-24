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
# from donate.models import (
#     Project,
#     Account,
# )

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

# this Project class and fake_projects can be deleted once we get the database working
class Project:
    def __init__(self, name, amount, goal):
        self.name = name
        self.amount = amount
        self.goal = goal

class Donation:
    def __init__(self, name, amount, project=None):
        self.name = name
        self.amount = amount
        self.project = project

FAKE_PROJECTS = [
    Project("laser", 2000, 5000),
    Project("Forever Home", 2000, 4000000),
    Project("printer", 150, 200),
    Project("Fire Drill 2018", 200, None),
    Project("Axidraw", 222, 200)
]
FAKE_RECENT_DONATIONS = [
    Donation("Brad Pitt", 4, None),
    Donation("Matthew Arcidy", 3, "Club Mate"),
    Donation("Angelina Jolie", 4, "Whatever"),
    Donation("Bill Gates", 5, "Club Mate")
]

@home_page.route('/')
@home_page.route('/index')
def index():
    data = {'title': "New Donate.  Like Old Donate.  Only New."}
    return render_template('main.html',
                           title="New Donate",
                           data=data,
                           git_sha=git.Repo(search_parent_directories=True).head.object.hexsha,
                           repo_path="https://github.com/marcidy/nb_donate/commits/",
                           projects=FAKE_PROJECTS,
                           recent_donations=FAKE_RECENT_DONATIONS
                           )


@projects_page.route('/projects')
def projects():
    # projects = db.session.query(Project)
    # return (render_template('projects.html',
    #                         title='Projects',
    #                         projects=projects))
    return (render_template('projects.html',
                            title='Projects',
                            projects=FAKE_PROJECTS))


# Delete this once the database is set up
def find_project(project_name):
    for project in FAKE_PROJECTS:
        if project.name.lower().replace(" ","_") == project_name.lower():
            return [project]
    return []


@project_page.route('/projects/<project_name>')
def get_project(project_name):
    # project = db.session.query(Project).filter_by(name == project_name)
    project = find_project(project_name)
    if len(project) == 0:
        redirect(url_for('new_project', project_name=project_name))
    if len(project) == 1:
        return (render_template('project.html',
                                title=project_name,
                                project=project[0]))
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
