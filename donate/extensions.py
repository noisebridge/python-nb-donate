from flask_sqlalchemy import SQLAlchemy, Model
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
