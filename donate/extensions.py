from flask_sqlalchemy import SQLAlchemy, Model
from flask_migrate import Migrate


''' loadLall app extensions '''
db = SQLAlchemy()
migrate = Migrate()
