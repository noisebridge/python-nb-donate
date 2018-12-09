from sqlalchemy.orm import relationship
from .extensions import db

Column = db.Column
relationship = relationship
Model = db.Model
