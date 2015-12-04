from sqlalchemy import create_engine, literal
from os import path
db_path = "sqlite:///" + path.expanduser("~/solutions.db")
engine = create_engine(db_path, echo=False)

from common_classes import Animal, Genotype, Solution, ChronicTreatmentAdministration, ChronicTreatment, Weight

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
for row in session.query(Animal).order_by(Animal.id):
	print row.id_uzh, row.id_eth, row.id
	for row in row.weight:
		print row.weight
	# for row1 in row.administrations:
	# 	print row1.date

session.close()
engine.dispose()
