from sqlalchemy import create_engine, literal
from os import path
from query import loadSession

db_path = "~/meta.db"

import pandas as pd

from common_classes import *

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker

session, engine = loadSession(db_path)
# for row in session.query(Animal).order_by(Animal.id):
# 	print row.id_uzh, row.id_eth, row.id
# 	for row in row.weight:
# 		print row.weight
	# for row1 in row.administrations:
	# 	print row1.date

sql_query=session.query(Incubation)
for i in [["revolutions_per_minute",1000],["duration",60]]:
	sql_query = sql_query.filter(getattr(Incubation, i[0])==i[1])
# sql_query=session.query(Incubation).filter(getattr(Incubation, "revolutions_per_minute")==1000).filter(getattr(Incubation, "duration")==60)
mystring = sql_query.statement
mydf = pd.read_sql_query(mystring,engine)
print(mydf)

# for i in session.query(Incubation).filter(Incubation.revolutions_per_minute == 1000):
# 	for a in i.fmri_measurements:
# 		print(a)

# sub_query = session.query(Animal.id, ChronicTreatment)
# sql_query = session.query(Animal.treatment).filter(ChronicTreatment.code == "chrFlu")

# EXAMPLE: select animals with a certain field of a certain field
# sql_query = session.query(Animal).join(Animal.treatments).filter(ChronicTreatment.code == "chrFlu")
# for item in sql_query:
# 	pass
# mystring = str(sql_query)
# mydf = pd.read_sql_query(mystring,engine,params=["chrFlu"])


# sql_query = session.query(Animal).order_by(Animal.cage_eth)
# for item in sql_query:
# 	pass
# mystring = str(sql_query)
# mydf = pd.read_sql_query(mystring,engine)
# print(mydf)


session.close()
engine.dispose()
