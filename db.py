from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ensure all our models are registered
import models.exercise  # noqa
import models.food  # noqa
