#!/usr/bin/python

import argh
import json
import sys

import pandas as pd

from datetime import *
from sqlalchemy import create_engine, literal, or_, inspection
from os import path
from .common_classes import *
from sqlalchemy.orm import sessionmaker, aliased
import sqlalchemy


allowed_classes = {
	"Animal": Animal,
	"Cage": Cage,
	"CageStay": CageStay,
	"DrinkingMeasurement": DrinkingMeasurement,
	"DNAExtractionProtocol": DNAExtractionProtocol,
	"Evaluation": Evaluation,
	"ForcedSwimTestMeasurement": ForcedSwimTestMeasurement,
	"FMRIMeasurement": FMRIMeasurement,
	"FMRIScannerSetup": FMRIScannerSetup,
	"FMRIAnimalPreparationProtocol": FMRIAnimalPreparationProtocol,
	"Genotype": Genotype,
	"HandlingHabituationProtocol": HandlingHabituationProtocol,
	"HandlingHabituation": HandlingHabituation,
	"Ingredient": Ingredient,
	"Irregularity": Irregularity,
	"Incubation": Incubation,
	"LaserStimulationProtocol": LaserStimulationProtocol,
	"MeasurementUnit": MeasurementUnit,
	"Operator": Operator,
	"Substance": Substance,
	"SucrosePreferenceMeasurement": SucrosePreferenceMeasurement,
	"Solution": Solution,
	"Treatment": Treatment,
	"TreatmentProtocol": TreatmentProtocol,
	"Weight": Weight,
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

def add_all_columns(cols, class_name):
	joinclassobject = allowed_classes[class_name]

	#we need to catch this esception, because for aliased classes a mapper is not directly returned
	try:
		col_name_cols = inspection.inspect(joinclassobject).columns.items()
	except AttributeError:
		col_name_cols = inspection.inspect(joinclassobject).mapper.columns.items()

	for col_name, col in col_name_cols:
		column = getattr(joinclassobject, col.key)
		cols.append(column.label("{}_{}".format(class_name, col_name)))

def get_df(db_path, col_entries=[], join_entries=[], filters=[], outerjoin=False):
	"""Return a dataframe from a complex query of a LabbookDB-style database

	Arguments
	---------

	db_path : string
		Path to database file.
	col_entries : list
		A list of tuples containing the columns to be queried:
		* 1-tuples indicate all attributes of a class are to be queried
		* 2-tuples indicate only the attribute specified by the second element, of the class specified by the first element is to be queried
		* 3-tuples indicate that an aliased class of the type given by the second element is to be created and named according to the first and second elements, separated by an underscore. The attribute given by the third element will be queried; if the thid element is empty, all attributes will be queried
	join_entries : list
		A list of tuples specifying the desired join operations:
		* 1-tuples give the join
		* 2-tuples give the class to be joined on the first element, and the explicit relationship (attribute of another class) on the second element
		If any of the elements contains a period, the expression will be evaluated as a class (preceeding the period) attribute (after the period)$
	filters : list
		A list of lists giving filters for the query. In each sub-list the first and second elements give the class and attribute to be matched. Every following element specifies a possible value for the class attribute (implemented as inclusive disjunction). If the attribute name ends in "date" the function compute datetime objects from the subsequent strings containing numbers separated by commas.



	Examples
	--------
	>>> col_entries=[
			("Animal","id"),
			("Treatment",),
			("FMRIMeasurement",),
			("TreatmentProtocol","code"),
			("Cage","id"),
			("Cage","Treatment",""),
			("Cage","TreatmentProtocol","code")
			]
	>>> join_entries=[
			("Animal.treatments",),
			("FMRIMeasurement",),
			("Treatment.protocol",),
			("Animal.cage_stays",),
			("CageStay.cage",),
			("Cage_Treatment","Cage.treatments"),
			("Cage_TreatmentProtocol","Cage_Treatment.protocol")
			]
	>>> filters = [["Cage_Treatment","start_date","2016,4,25,19,30"]]
	>>> reference_df = get_df("~/syncdata/meta.db",col_entries=col_entries, join_entries=join_entries, filters=filters)

	"""


	session, engine = loadSession(db_path)

	cols=[]
	for col_entry in col_entries:
		if len(col_entry) == 1:
			add_all_columns(cols, col_entry[0])
		if len(col_entry) == 2:
			cols.append(getattr(allowed_classes[col_entry[0]],col_entry[1]).label("{}_{}".format(*col_entry)))
		if len(col_entry) == 3:
			aliased_class = aliased(allowed_classes[col_entry[1]])
			allowed_classes[col_entry[0]+"_"+col_entry[1]] = aliased_class
			if col_entry[2] == "":
				add_all_columns(cols, col_entry[0]+"_"+col_entry[1])
			else:
				cols.append(getattr(aliased_class,col_entry[2]).label("{}_{}_{}".format(*col_entry)))

	joins=[]
	for join_entry in join_entries:
		join_parameters = []
		for join_entry_substring in join_entry:
			if "." in join_entry_substring:
				class_name, table_name = join_entry_substring.split(".") #if this unpacks >2 values, the user specified strings are malformed
				join_parameters.append(getattr(allowed_classes[class_name],table_name))
			else:
				join_parameters.append(allowed_classes[join_entry_substring])
		joins.append(join_parameters)

	sql_query = session.query(*cols)
	for join in joins:
		if outerjoin:
			sql_query = sql_query.outerjoin(*join)
		else:
			sql_query = sql_query.join(*join)

	for sub_filter in filters:
		if sub_filter:
			if sub_filter[1][-4:] == "date" and isinstance(sub_filter[2], str):
				for ix, i in enumerate(sub_filter[2:]):
					sub_filter[2+ix] = datetime(*[int(a) for a in i.split(",")])
			if len(sub_filter) == 3:
				sql_query = sql_query.filter(getattr(allowed_classes[sub_filter[0]], sub_filter[1]) == sub_filter[2])
			else:
				sql_query = sql_query.filter(or_(getattr(allowed_classes[sub_filter[0]], sub_filter[1]) == v for v in sub_filter[2:]))

	mystring = sql_query.statement
	df = pd.read_sql_query(mystring,engine)
	session.close()
	engine.dispose()

	return df

	#THIS IS KEPT TO REMEMBER WHENCE THE ABOVE AWKWARD ROUTINES CAME AND HOW THE CODE IS SUPPOSED TO LOOK IF TYPED OUT
	# CageTreatment = aliased(Treatment)
	# CageTreatmentProtocol = aliased(TreatmentProtocol)
	# sql_query = session.query(
	# 						Animal.id.label("Animal_id"),
	# 						TreatmentProtocol.code.label("TreatmentProtocol_code"),
	# 						Cage.id.label("Cage_id"),
	# 						CageTreatment.id.label("Cage_Treatment_id"),
	# 						CageTreatmentProtocol.code.label("Cage_TreatmentProtocol_code"),
	# 						)\
	# 				.join(Animal.treatments)\
	# 				.join(Treatment.protocol)\
	# 				.join(Animal.cage_stays)\
	# 				.join(CageStay.cage)\
	# 				.join(CageTreatment, Cage.treatments)\
	# 				.join(CageTreatmentProtocol, CageTreatment.protocol)\
	# 				.filter(Animal.id == 43)
	# mystring = sql_query.statement
	# reference_df = pd.read_sql_query(mystring,engine)
	# print reference_df.columns
	# print reference_df
