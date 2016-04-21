#!/usr/bin/python

from datetime import datetime
import argh
import json
import sys
import numpy

import pandas as pd

from sqlalchemy import create_engine, literal, update, insert
from os import path
from common_classes import *
from sqlalchemy.orm import sessionmaker
import sqlalchemy

allowed_classes = {
	"Animal": Animal,
	"Cage": Cage,
	"CageStay": CageStay,
	"Treatment": Treatment,
	"DNAExtractionProtocol": DNAExtractionProtocol,
	"FMRIMeasurement": FMRIMeasurement,
	"FMRIScannerSetup": FMRIScannerSetup,
	"FMRIAnimalPreparationProtocol": FMRIAnimalPreparationProtocol,
	"Genotype": Genotype,
	"HandlingHabituationProtocol": HandlingHabituationProtocol,
	"HandlingHabituation": HandlingHabituation,
	"Ingredient": Ingredient,
	"Incubation": Incubation,
	"LaserStimulationProtocol": LaserStimulationProtocol,
	"MeasurementUnit": MeasurementUnit,
	"Operator": Operator,
	"Substance": Substance,
	"Solution": Solution,
	"TreatmentProtocol": TreatmentProtocol,
	"Weight": Weight,
	}

def loadSession(db_path):
	db_path = "sqlite:///" + path.expanduser(db_path)
	engine = create_engine(db_path, echo=False)
	Session = sessionmaker(bind=engine)
	session = Session()
	Base.metadata.create_all(engine)
	return session, engine

def add_to_db(session, engine, myobject):
	session.add(myobject)
	try:
		session.commit()
	except sqlalchemy.exc.IntegrityError:
		print("Please make sure this was not a double entry.")
	theid=myobject.id
	return(theid)

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

def update_parameter(db_path, entry_identification, parameters):
	"""Assigns a value to a givn parameter of a given entry
	"""

	if isinstance(parameters, str):
		parameters = json.loads(parameters)

	session, engine = loadSession(db_path)

	entry_class = allowed_classes[entry_identification.split(":")[0]]
	my_id = get_related_id(db_path, entry_identification)[0]

	for key in parameters:
		session.query(entry_class).\
			filter(entry_class.id == my_id).\
			update({key: parameters[key]})
	commit_and_close(session, engine)

def add_generic(db_path, parameters, walkthrough=False, session=None, engine=None):
	"""Adds new entries based on a parameter dictionary
	"""
	if not (session and engine) :
		session, engine = loadSession(db_path)
		close = True
	else:
		close = False
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
		if key[-4:] == "date":
			parameters[key] = datetime(*[int(i) for i in parameters[key].split(",")])
		if key[-3:] == "_id":
			try:
				input_values = get_related_id(session, engine, parameters[key])
			except ValueError:
				instructions("table_identifier")
			for input_value in input_values:
				input_value = int(input_value)
				setattr(myobject, key, input_value)
		#this triggers on-the-fly related entry creation:
		elif isinstance(parameters[key], list):
			related_entries=[]
			for related_entry in parameters[key]:
				if isinstance(related_entry, dict):
					related_entry, _ = add_generic(db_path, related_entry, session=session, engine=engine)
					session.add(myobject) # voodoo (imho) fix for the weird errors about myobject not being attached to a Session
					related_entries.append(related_entry)
				elif isinstance(related_entry, str):
					my_id = get_related_id(session, engine, related_entry)[0]
					entry_class = allowed_classes[related_entry.split(":")[0]]
					related_entry = session.query(entry_class).\
						filter(entry_class.id == my_id).all()[0]
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

	object_id = add_to_db(session, engine, myobject)
	if close:
		session.close()
		engine.dispose()
	return myobject, object_id


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
	# add_generic("~/meta.db", parameters={"CATEGORY":"Animal", "id_eth":4001, "id_uzh":"M2763", "sex":"f", "ear_punches":"LR",
		# "genotypes":["Genotype:code.eptg"]
		# })
	# update_parameter("~/meta.db", entry_identification="Cage:id_local.570974", parameters={"location":"AFS7pua"})
	argh.dispatch_command(add_generic)
