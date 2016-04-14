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
	"animal": Animal,
	"cage": Cage,
	"measurementunit": MeasurementUnit,
	"operator": Operator,
	"substance": Substance,
	"solution": Solution,
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
	commit_and_close(session, engine)

def add_genotype(name, zygosity):
	session, engine = loadSession()
	new_genotype = Genotype(name=name, zygosity=zygosity)
	session.add(new_animal)
	commit_and_close(session, engine)

def add_animal(db_path, id_eth, cage_eth, sex, ear_punches, id_uzh="", cage_uzh=""):
	if id_uzh:
		if double_entry(db_path, "id_uzh", id_uzh): return

	add_to_db(db_path, Animal(id_eth=id_eth, cage_eth=cage_eth, sex=sex, ear_punches=ear_punches, id_uzh=id_uzh, cage_uzh=cage_uzh))

def add_generic(db_path, category, walkthrough=False, parameters=""):
	"""Adds new entries based on a parameter dictionary
	"""

	category_class = allowed_classes[category]

	#detrmine class attributes
	attributes = dir(category_class())
	filtered_attributes = [i for i in attributes if i[0] != "_"]

	if not walkthrough:
		if not parameters:
			message = "You can list the following keys as part of your parameters: " + ", ".join(filtered_attributes)
			return message
		elif isinstance(parameters, dict):
			pass
		else:
			parameters = json.loads(parameters)

		myobject = category_class()
		for key in parameters:
			if key[-3:] == "_id":
				try:
					category, field, value = parameters[key].split(".")
				except ValueError:
					print("Make sure you have entered the value for \'"+key+"\' correctly. This value is supposed to refer to the id column of another table and needs to be specified as \'table_identifier\'.\'field_by_which_to_filter\'.\'target_value\'")
					continue
				session, engine = loadSession(db_path)
				sql_query=session.query(allowed_classes[category]).filter(getattr(allowed_classes[category], field)==value)
				mystring = sql_query.statement
				mydf = pd.read_sql_query(mystring,engine)
				related_table_ids = mydf["id"]
				input_values = list(related_table_ids)
				session.close()
				engine.dispose()
				for input_value in input_values:
					input_value = int(input_value)
					setattr(myobject, key, input_value)
			else:
				setattr(myobject, key, parameters[key])
	else:
		myobject = category_class()
		for key in filtered_attributes:
			if key == "id":
				continue
			value = raw_input("Enter your desired \""+key+"\" value:").decode(sys.stdin.encoding)
			print(value, type(value))
			setattr(myobject, key, value)

	add_to_db(db_path, myobject)


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
