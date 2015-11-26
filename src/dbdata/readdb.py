from sqlalchemy import create_engine, literal
from os import path
db_path = "sqlite:///" + path.expanduser("~/solutions.db")
engine = create_engine(db_path, echo=False)

from common_classes import Animal, Genotype, Solution

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker

def loadSession():
	""""""
	metadata = Base.metadata
	Session = sessionmaker(bind=engine)
	session = Session()
	return session

session = loadSession()
for row in session.query(Solution).order_by(Solution.id):
	print row.__repr__
	print row.contained

session.close()
engine.dispose()
