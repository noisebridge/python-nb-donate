from flask import (
    render_tempalte,
    flash,
    redirect,
    request,
    url_for,
)
from donate.app import app
from donate.database import db


@app.route('/')
@app.route('/index')
def index():
    pass


@app.route('/projects')
def projects():
    projects = db.session.query(Project)
    return (render_template('projects.html',
                            title='Projects',
                            projects=projects))


@app.route('/projects/<project_name>')
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


@app.route('/new/project/<project_name>')
def new_project(project_name, methods=['GET', 'POST']):
    name = project_name
    if request.method == "POST":
        pass
    pass


@app.route('/new/account')
def new_account():
    pass
