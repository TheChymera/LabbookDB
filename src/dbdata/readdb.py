from sqlalchemy import create_engine, literal
from os import path
db_path = "sqlite:///" + path.expanduser("~/meta.db")
engine = create_engine(db_path, echo=False)

import pandas as pd

from common_classes import Animal, Genotype, Solution, ChronicTreatmentAdministration, ChronicTreatment, Weight, FMRIMeasurement, ChronicTreatment

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker

def loadSession():
	""""""
	Session = sessionmaker(bind=engine)
	session = Session()
	return session

session = loadSession()
# for row in session.query(Animal).order_by(Animal.id):
# 	print row.id_uzh, row.id_eth, row.id
# 	for row in row.weight:
# 		print row.weight
	# for row1 in row.administrations:
	# 	print row1.date

# for i in session.query(Animal).filter(Animal.id_eth == 4001):
# 	for a in i.fmri_measurements:
# 		print a.date

# sub_query = session.query(Animal.id, ChronicTreatment)


# sql_query = session.query(Animal.treatment).filter(ChronicTreatment.code == "chrFlu")

sql_query = session.query(Animal).join(Animal.treatments).filter(ChronicTreatment.code == "chrFlu")

# subq = session.query(Animal.id).subquery()
# sql_query = session.query(ChronicTreatment).join((subq, subq.c.treatment_id=="chrFlu"))
for item in sql_query:
	pass

mystring = str(sql_query)
mydf = pd.read_sql_query(mystring,engine,params=["chrFlu"])
# print mydf.index[1]
# print mydf[["animals_id_uzh","animals_id_eth"]]
print mydf
# print mydf.columns[["animals_id_uzh","animals_id_eth"]]


session.close()
engine.dispose()
