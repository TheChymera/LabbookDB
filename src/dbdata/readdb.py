from sqlalchemy import create_engine, literal
from os import path
db_path = "sqlite:///" + path.expanduser("~/solutions.db")
engine = create_engine(db_path, echo=False)

from common_classes import Animal, Genotype, Solution, ChronicTreatmentAdministration, ChronicTreatment

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
for row in session.query(ChronicTreatment).order_by(ChronicTreatment.code):
	print row.name
	for row1 in row.administrations:
		print row1.date

session.close()
engine.dispose()
