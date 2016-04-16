#!/usr/bin/python

import datetime
import argh
import json
import sys
import numpy

import pandas as pd

from sqlalchemy import create_engine, literal
from os import path
from common_classes import *
from sqlalchemy.orm import sessionmaker
import sqlalchemy

allowed_classes = {
	"Animal": Animal,
	"Cage": Cage,
	"Treatment": Treatment,
	"DNAExtractionProtocol": DNAExtractionProtocol,
	"FMRIScannerSetup": FMRIScannerSetup,
	"FMRIAnimalPreparationProtocol": FMRIAnimalPreparationProtocol,
	"HandlingHabituationProtocol": HandlingHabituationProtocol,
	"Ingredient": Ingredient,
	"Incubation": Incubation,
	"LaserStimulationProtocol": LaserStimulationProtocol,
	"MeasurementUnit": MeasurementUnit,
	"Operator": Operator,
	"Substance": Substance,
	"Solution": Solution,
	"TreatmentProtocol": TreatmentProtocol,
	}

def loadSession(db_path):
	db_path = "sqlite:///" + path.expanduser(db_path)
	engine = create_engine(db_path, echo=False)
	Session = sessionmaker(bind=engine)
	session = Session()
	Base.metadata.create_all(engine)
	return session, engine

def add_to_db(db_path, myobject):
	session, engine = loadSession(db_path)
	session.add(myobject)
	try:
		session.commit()
	except sqlalchemy.exc.IntegrityError:
		print("Please make sure this was not a double entry.")
	theid=myobject.id
	session.close()
	engine.dispose()
	return(theid)

def add_genotype(name, zygosity):
	session, engine = loadSession()
	new_genotype = Genotype(name=name, zygosity=zygosity)
	session.add(new_animal)
	commit_and_close(session, engine)

def add_animal(db_path, id_eth, cage_eth, sex, ear_punches, id_uzh="", cage_uzh=""):
	if id_uzh:
		if double_entry(db_path, "id_uzh", id_uzh): return

	add_to_db(db_path, Animal(id_eth=id_eth, cage_eth=cage_eth, sex=sex, ear_punches=ear_punches, id_uzh=id_uzh, cage_uzh=cage_uzh))

def instructions(kind):
	if kind == "table_identifier":
		print("Make sure you have entered the filter value correctly. This value is supposed to refer to the id column of another table and needs to be specified as \'table_identifier\'.\'field_by_which_to_filter\'.\'target_value\'")

def get_related_id(db_path, parameters):
	session, engine = loadSession(db_path)
	category = parameters.split(":",1)[0]
	sql_query=session.query(allowed_classes[category])
	for field_value in parameters.split(":",1)[1].split("&&"):
		field, value = field_value.split(".",1)
		values=None
		if ":" in value:
			values = get_related_id(db_path, value)
		if values:
			for value in values:
				sql_query = sql_query.filter(getattr(allowed_classes[category], field)==value)
				print("AAAA", field, value)
		else:
			sql_query = sql_query.filter(getattr(allowed_classes[category], field)==value)
			print("BBBB", field, value)
	mystring = sql_query.statement
	print("STRING:",mystring)
	mydf = pd.read_sql_query(mystring,engine)
	#Dirty hack:
	if mydf.groupby(mydf.columns, axis=1).agg(numpy.max) != mydf.groupby(mydf.columns, axis=1).agg(numpy.max):
		raise
	else:
		mydf = related_table_ids.groupby(mydf.columns, axis=1).agg(numpy.max)
	print(parameters, mydf)
	related_table_ids = mydf["id"]
	print(related_table_ids)
	input_values = list(related_table_ids)
	if input_values == []:
		print("No entry was found with a value of \""+value+"\" on the \""+field+"\" column of the \""+category+"\" CATEGORY, in the database located under "+db_path+".")
	session.close()
	engine.dispose()
	return input_values

def add_generic(db_path, parameters, walkthrough=False):
	"""Adds new entries based on a parameter dictionary
	"""

	if isinstance(parameters, str):
		parameters = json.loads(parameters)

	category_class = allowed_classes[parameters["CATEGORY"]]
	if list(parameters.keys()) == ["CATEGORY"]:
		attributes = dir(category_class())
		filtered_attributes = [i for i in attributes if i[0] != "_"]
		print("You can list the following keys as part of your parameters: " + ", ".join(filtered_attributes))
	parameters.pop("CATEGORY", None)

	myobject = category_class()
	for key in parameters:
		if key[-3:] == "_id":
			try:
				input_values = get_related_id(db_path, parameters[key])
			except ValueError:
				instructions("table_identifier")
			for input_value in input_values:
				print(myobject, key, input_value)
				input_value = int(input_value)
				setattr(myobject, key, input_value)
		#this triggers on-the-fly related entry creation:
		elif isinstance(parameters[key], list) and isinstance(parameters[key][0], dict):
			related_entries=[]
			for related_entry in parameters[key]:
				related_entry, _ = add_generic(db_path, related_entry)
				related_entries.append(related_entry)
			setattr(myobject, key, related_entries)
		else:
			setattr(myobject, key, parameters[key])
		# Walkthrough Legacy Code:
		# myobject = category_class()
		# for key in filtered_attributes:
		# 	if key == "id":
		# 		continue
		# 	value = raw_input("Enter your desired \""+key+"\" value:").decode(sys.stdin.encoding)
		# 	setattr(myobject, key, value)

	return myobject, add_to_db(db_path, myobject)


def commit_and_close(session, engine):
	try:
		session.commit()
	except sqlalchemy.exc.IntegrityError:
		print("Please make sure this was not a double entry.")
	session.close()
	engine.dispose()

def double_entry(db_path, field, value):
	session, engine = loadSession(db_path)
	q=session.query(Animal).filter(getattr(Animal, field)==value)
	if session.query(literal(True)).filter(q.exists()).scalar():
		session.close()
		engine.dispose()
		print("Entry conflict for key "+field+" = "+value)
		return True
	session.close()
	engine.dispose()


if __name__ == '__main__':
	argh.dispatch_command(add_generic)
	# add_generic("~/meta.db", "animal")
	# add_animal("~/animal.db", 4011, 4, "f", "2L", id_uzh="M2760", cage_uzh="570971")
