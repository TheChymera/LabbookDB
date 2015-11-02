from sqlalchemy import create_engine
from os import path
db_path = "sqlite:///" + path.expanduser("~/data.db")
engine = create_engine(db_path, echo=False)

from common_classes import Animal, Genotype

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
a=0
for row in session.query(Animal).order_by(Animal.id):
	a+= 1
	print a
