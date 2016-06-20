#!/usr/bin/python

import datetime
import argh
import json
import sys

import pandas as pd

from sqlalchemy import create_engine, literal
from os import path
from common_classes import *
from sqlalchemy.orm import sessionmaker
import sqlalchemy

allowed_classes = {
	"Animal": Animal,
	"Cage": Cage,
	"DNAExtractionProtocol": DNAExtractionProtocol,
	"FMRIScannerSetup": FMRIScannerSetup,
	"FMRIAnimalPreparationProtocol": FMRIAnimalPreparationProtocol,
	"HandlingHabituationProtocol": HandlingHabituationProtocol,
	"Ingredient": Ingredient,
	"Incubation": Incubation,
	"MeasurementUnit": MeasurementUnit,
	"Operator": Operator,
	"Substance": Substance,
	"Solution": Solution,
	}

def instructions(kind):
	if kind == "table_identifier":
		print("Make sure you have entered the filter value correctly. This value is supposed to refer to the id column of another table and needs to be specified as \'table_identifier\'.\'field_by_which_to_filter\'.\'target_value\'")

def get_related_id(session, engine, parameters):
	category = parameters.split(":",1)[0]
	sql_query=session.query(allowed_classes[category])
	for field_value in parameters.split(":",1)[1].split("&&"):
		field, value = field_value.split(".",1)
		if ":" in value:
			values = get_related_id(session, engine, value)
			for value in values:
				value=int(value) # the value is returned as a numpy object
				if field[-4:] == "date": # support for date entry matching (the values have to be passes as string but matched as datetime)
					value = datetime(*[int(i) for i in value.split(",")])
				sql_query = sql_query.filter(getattr(allowed_classes[category], field)==value)
		else:
			if field[-4:] == "date": # support for date entry matching (the values have to be passes as string but matched as datetime)
				value = datetime(*[int(i) for i in value.split(",")])
			sql_query = sql_query.filter(getattr(allowed_classes[category], field)==value)
	mystring = sql_query.statement
	mydf = pd.read_sql_query(mystring,engine)
	mydf = mydf.T.groupby(level=0).first().T #awkward hack to deal with polymorphic tables returning multiple IDs
	related_table_ids = mydf["id"]
	input_values = list(related_table_ids)
	if input_values == []:
		raise BaseException("No entry was found with a value of \""+str(value)+"\" on the \""+field+"\" column of the \""+category+"\" CATEGORY, in the database.")
	session.close()
	engine.dispose()
	return input_values

def simple_query(db_path, category, field, value, mask="", first=True):
	session, engine = loadSession(db_path)
	sql_query=session.query(allowed_classes[category]).filter(getattr(allowed_classes[category], field)==value)
	print(sql_query.all()[0].__repr__)
	mystring = sql_query.statement
	mydf = pd.read_sql_query(mystring,engine)
	if mask:
		mydf = mydf[mask]
	if first:
		mydf = mydf[0]
	print(mydf)
	session.close()
	engine.dispose()

def loadSession(db_path):
	db_path = "sqlite:///" + path.expanduser(db_path)
	engine = create_engine(db_path, echo=False)
	Session = sessionmaker(bind=engine)
	session = Session()
	Base.metadata.create_all(engine)
	return session, engine

def commit_and_close(session, engine):
	try:
		session.commit()
	except sqlalchemy.exc.IntegrityError:
		print("Please make sure this was not a double entry.")
	session.close()
	engine.dispose()



if __name__ == '__main__':
	# argh.dispatch_command(add_generic)
	simple_query("~/meta.db", "Solution", "code", "med-sal", first=False)
	# add_animal("~/animal.db", 4011, 4, "f", "2L", id_uzh="M2760", cage_uzh="570971")
