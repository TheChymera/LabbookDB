#!/usr/bin/python
from __future__ import print_function

import argh
import json
import numpy

import pandas as pd

from sqlalchemy import create_engine, literal, update, insert
from os import path
from sqlalchemy.orm import sessionmaker
import sqlalchemy

from .common_classes import *
from .query import ALLOWED_CLASSES

def load_session(db_path):
	"""Load and return a new SQLalchemy session and engine.

	Parameters
	----------
	db_path : str
		Path to desired database location, can be relative or use tilde to specify the user $HOME.

	Returns
	-------
	session : sqlalchemy.orm.session.Session
		Session instance.
	engine : sqlalchemy.engine.Engine
		Engine instance.
	"""

	db_path = "sqlite:///" + path.abspath(path.expanduser(db_path))
	engine = create_engine(db_path, echo=False)
	#it is very important that `autoflush == False`, otherwise if "treatments" or "measurements" entried precede "external_ids" the latter will insert a null on the animal_id column
	Session = sessionmaker(bind=engine, autoflush=False)
	session = Session()
	Base.metadata.create_all(engine)
	return session, engine

def add_to_db(session, engine, myobject):
	"""Add an object to session and return the .id attribute value.

	Parameters
	----------
	session : sqlalchemy.orm.session.Session
		Session instance, as created with labbookdb.db.add.load_session().
	engine : sqlalchemy.engine.Engine
		Engine instance correponding to the Session instance under session, as created with labbookdb.db.add.load_session().
	myobject : object
		LabbookDB object with SQLAlchemy-compatible attributes (e.g. as found under labbookdb.db.common_classes).

	Returns
	-------
	theid : int
		Value of myobject.id attribute
	"""

	session.add(myobject)
	try:
		session.commit()
	except sqlalchemy.exc.IntegrityError:
		print("Please make sure this was not a double entry:", myobject)
	theid=myobject.id
	return(theid)

def instructions(kind):
	"""Print helpful instructions for common error-causing input issues

	Parameters
	----------
	kind : {"table_identifier",}
		Shorthand for the instructin message to be printed.
	"""
	if kind == "table_identifier":
		print("Make sure you have entered the filter value correctly. This value is supposed to refer to the id column of another table and needs to be specified as \'table_identifier\'.\'field_by_which_to_filter\'.\'target_value\'")

def get_related_ids(session, engine, parameters):
	category = parameters.split(":",1)[0]
	sql_query=session.query(ALLOWED_CLASSES[category])
	for field_value in parameters.split(":",1)[1].split("&&"):
		field, value = field_value.split(".",1)
		# this unpacks one level of AND separators.
		# we use this so that "Animal:external_ids.AnimalExternalIdentifier:database.ETH/AIC/cdb&#&identifier.275511" will look for both the database and the identifier attributes in the AnimalExternalIdentifier class.
		# if we use "Animal:external_ids.AnimalExternalIdentifier:database.ETH/AIC/cdb&#&identifier.275511" that will look for the database attribute on the AnimalExternalIdentifier class, and for the identifier attribute on the Animal class.
		if "&#&" in value or "&##&" in value:
			value=value.replace("&#&", "&&")
			value=value.replace("&##&", "&#&")
		if ":" in value:
			values, objects = get_related_ids(session, engine, value)
			for value in values:
				value=int(value) # the value is returned as a numpy object
				if field[-4:] == "date": # support for date entry matching (the values have to be passes as string but matched as datetime)
					value = datetime.datetime(*[int(i) for i in value.split(",")])
				# we are generally looking to match values, but sometimes the parent table does not have an id column, but only a relationship column (e.g. in one to many relationships)
				try:
					sql_query = sql_query.filter(getattr(ALLOWED_CLASSES[category], field)==value)
				except sqlalchemy.exc.InvalidRequestError:
					sql_query = sql_query.filter(getattr(ALLOWED_CLASSES[category], field).contains(*[i for i in objects]))
		else:
			if field[-4:] == "date": # support for date entry matching (the values have to be passes as string but matched as datetime)
				value = datetime.datetime(*[int(i) for i in value.split(",")])
			sql_query = sql_query.filter(getattr(ALLOWED_CLASSES[category], field)==value)
	mystring = sql_query.with_labels().statement
	mydf = pd.read_sql_query(mystring,engine)
	category_tablename = ALLOWED_CLASSES[category].__table__.name
	related_table_ids = mydf[category_tablename+"_id"]
	input_values = list(related_table_ids)
	input_values = [int(i) for i in input_values]
	if input_values == []:
		raise BaseException("No entry was found with a value of \""+str(value)+"\" on the \""+field+"\" column of the \""+category+"\" CATEGORY, in the database.")
	session.close()
	engine.dispose()
	return input_values, sql_query

def append_parameter(db_path, entry_identification, parameters):
	"""Assigns a value to a given parameter of a given entry.

	Parameters
	----------

	db_path : str
		A string especifying the database path

	entry_identification : str
		A LabbookDB syntax string specifying an instance of an object for which to update a parameter.
		Example strings: "Animal:external_ids.AnimalExternalIdentifier:database.ETH/AIC&#&identifier.5701" , "Cage:id.14"

	parameters : dict
		A dictionary where keys are strings giving the names of attributes of the class selected by entry_identification, and values are either the values to assign (verbatim: string, int, or float) or LabbookDB syntax strings specifying a related entry, or a list of LabbookDB syntax strings specifying related entries, or a list of LabbookDB-style dictionaries specifying new entries to be created and linked.
	"""

	if isinstance(parameters, str):
		parameters = json.loads(parameters)

	session, engine = load_session(db_path)

	entry_class = ALLOWED_CLASSES[entry_identification.split(":")[0]]
	my_id = get_related_ids(session, engine, entry_identification)[0][0]
	myobject = session.query(entry_class).filter(entry_class.id == my_id)[0]

	for parameter_key in parameters:
		parameter_expression = parameters[parameter_key]
		if isinstance(parameter_expression, (str, int, float)):
			if ":" in parameter_expression and "." in parameter_expression:
				related_entry_ids, _ = get_related_ids(session, engine, i)
				related_entry_class = ALLOWED_CLASSES[i.split(":")[0]]
				for related_entry_id in related_entry_ids:
					related_entry = session.query(related_entry_class).filter(related_entry_class.id == related_entry_id)[0]
					setattr(myobject, parameter_key, related_entry)
			else:
				if parameter_key[-4:] == "date":
					parameter_expression = datetime.datetime(*[int(i) for i in parameter_expression.split(",")])
				setattr(myobject, parameter_key, parameter_expression)
		else:
			set_attribute = getattr(myobject, parameter_key)
			for parameter_expression_entry in parameter_expression:
				if isinstance(parameter_expression_entry, dict):
					new_entry, _ = add_generic(db_path, parameter_expression_entry, session=session, engine=engine)
					set_attribute.append(new_entry)
				elif isinstance(parameter_expression_entry, str):
					related_entry_ids, _ = get_related_ids(session, engine, parameter_expression_entry)
					related_entry_class = ALLOWED_CLASSES[parameter_expression_entry.split(":")[0]]
					for related_entry_id in related_entry_ids:
						related_entry = session.query(related_entry_class).filter(related_entry_class.id == related_entry_id)[0]
						set_attribute.append(related_entry)
	commit_and_close(session, engine)

def add_generic(db_path, parameters, session=None, engine=None):
	"""Adds new entries based on a LabbookDB-syntax parameter dictionary.

	Parameters
	----------
	db_path : str
		Path to database to open if session and engine parameters are not already passed, can be relative or use tilde to specify the user $HOME.
	parameters : str
		LabbookDB-syntax string specifying the entry class and attributes.
	session : sqlalchemy.orm.session.Session, optional
		Session instance, as created with labbookdb.db.add.load_session().
	engine : sqlalchemy.engine.Engine, optional
		Engine instance correponding to the Session instance under session, as created with labbookdb.db.add.load_session().

	Returns
	-------
	myobject : object
		LabbookDB object with SQLAlchemy-compatible attributes (e.g. as found under labbookdb.db.common_classes).
	object_id : int
		Value of myobject.id attribute.
	"""

	if not (session and engine) :
		session, engine = load_session(db_path)
		close = True
	else:
		close = False
	if isinstance(parameters, str):
		parameters = json.loads(parameters)

	category_class = ALLOWED_CLASSES[parameters["CATEGORY"]]
	if list(parameters.keys()) == ["CATEGORY"]:
		attributes = dir(category_class())
		filtered_attributes = [i for i in attributes if i[0] != "_"]
		print("You can list the following keys as part of your parameters: " + ", ".join(filtered_attributes))
	parameters.pop("CATEGORY", None)

	myobject = category_class()
	for key, _ in sorted(parameters.items()):
		if key[-4:] == "date":
			parameters[key] = datetime.datetime(*[int(i) for i in parameters[key].split(",")])
		if key[-3:] == "_id" and not isinstance(parameters[key], int):
			try:
				input_values, _ = get_related_ids(session, engine, parameters[key])
			except ValueError:
				instructions("table_identifier")
			for input_value in input_values:
				input_value = int(input_value)
				print("Setting", myobject.__class__.__name__+"'s",key,"attribute to",input_value)
				setattr(myobject, key, input_value)
		#this triggers on-the-fly related-entry creation:
		elif isinstance(parameters[key], list):
			related_entries=[]
			for related_entry in parameters[key]:
				if isinstance(related_entry, dict):
					related_entry, _ = add_generic(db_path, related_entry, session=session, engine=engine)
					related_entries.append(related_entry)
				elif isinstance(related_entry, str):
					my_id = get_related_ids(session, engine, related_entry)[0][0]
					entry_class = ALLOWED_CLASSES[related_entry.split(":")[0]]
					related_entry = session.query(entry_class).\
						filter(entry_class.id == my_id).all()[0]
					related_entries.append(related_entry)
			session.add(myobject) # voodoo (imho) fix for the weird errors about myobject not being attached to a Session
			print("Setting", myobject.__class__.__name__+"'s",key,"attribute to",related_entries)
			setattr(myobject, key, related_entries)
		else:
			print("Setting", myobject.__class__.__name__+"'s",key,"attribute to",parameters[key])
			setattr(myobject, key, parameters[key])

	object_id = add_to_db(session, engine, myobject)
	if close:
		session.close()
		engine.dispose()
	return myobject, object_id

def commit_and_close(session, engine):
	"""Commit and close session and dispose of engine.
	Nonfatal for sqlalchemy.exc.IntegrityError with print notification.

	Parameters
	----------
	session : sqlalchemy.orm.session.Session, optional
		Session instance, as created with labbookdb.db.add.load_session().
	engine : sqlalchemy.engine.Engine, optional
		Engine instance correponding to the Session instance under session, as created with labbookdb.db.add.load_session().
	"""

	try:
		session.commit()
	except sqlalchemy.exc.IntegrityError:
		print("Please make sure this was not a double entry.")
	session.close()
	engine.dispose()
