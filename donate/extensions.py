from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


''' loadLall app extensions '''
db = SQLAlchemy()
migrate = Migrate()
