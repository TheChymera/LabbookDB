from sqlalchemy import create_engine, literal
from os import path
db_path = "sqlite:///" + path.expanduser("~/animal_data.db")
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
for row in session.query(Animal).order_by(Animal.id_eth):
	print row.__repr__
	print row.sex

session.close()
engine.dispose()
