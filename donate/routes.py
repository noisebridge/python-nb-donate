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


'''
Project/Donation classes and FAKE_ data can be
deleted once we get the database working
'''


class Project:
    def __init__(self, name, amount, goal):
        self.name = name
        self.amount = amount
        self.goal = goal
        self.ccy = "USD"


class Donation:
    def __init__(self, name, amount, project=None):
        self.name = name
        self.amount = amount
        self.project = project


FAKE_PROJECTS = [
    Project("laser", 2000, 5000),
    Project("Forever Home", 2000, 4000000),
    Project("printer", 150, 200),
    Project("Fire Drill 2018", 200, 20000),
    Project("Axidraw", 222, 200),
    Project("Flaschen", 12, 5000),
    Project("Taschen", 52, 320),
    Project("Being Excellent", 1793, 2000),
    Project("Hello World", 97, 600),
    Project("Learning things", 672, 950),
    Project("Laser cutter", 0, 5250)
]
FAKE_RECENT_DONATIONS = [
    Donation("Mark Mothersbaugh", 89, "A really long project name"),
    Donation("Brad Pitt", 4, None),
    Donation("Matthew Arcidy", 3, "Club Mate"),
    Donation("Angelina Jolie", 4, "Whatever"),
    Donation("Bill Gates", 5, "Club Mate")
]
'''
end fake data
'''


@home_page.route('/')
@home_page.route('/index')
def index():
    projects = sorted(db.sesion.query(Project).all(),
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
    return render_template('thanks.html',
                           data={
                               'git_sha': git_sha,
                               'repo_path': repo_path
                           })


@projects_page.route('/projects')
def projects():
    projects = sorted(db.sesion.query(Project).all(),
                      key=lambda proj: proj.name)

    return render_template('projects.html',
                           title='Projects',
                           projects=sorted_projects)


@project_page.route('/projects/<project_name>')
def get_project(project_name):
    project = db.session.query(Project).filter_by(name == project_name)
    if len(project) == 0:
        return new_project(project_name)
    if len(project) == 1:
        return (render_template('project.html',
                                title=project_name,
                                project=project[0]))
    if len(project) > 1:
        raise ValueError("shit we're fucked in projects m8y!")


@new_project_page.route('/new/project/<project_name>', methods=['GET', 'POST'])
def new_project(project_name):
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
