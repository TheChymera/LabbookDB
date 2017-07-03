#!/usr/bin/python

import argh
import json
import sys

import pandas as pd

import datetime
from sqlalchemy import create_engine, literal, or_, inspection
from os import path
from sqlalchemy.orm import sessionmaker, aliased, contains_eager
import sqlalchemy

from .common_classes import *

ALLOWED_CLASSES = {
	"Animal": Animal,
	"AnimalExternalIdentifier": AnimalExternalIdentifier,
	"AnesthesiaProtocol": AnesthesiaProtocol,
	"Arena": Arena,
	"Cage": Cage,
	"CageStay": CageStay,
	"Biopsy": Biopsy,
	"BrainBiopsy": BrainBiopsy,
	"BrainExtractionProtocol": BrainExtractionProtocol,
	"DrinkingMeasurement": DrinkingMeasurement,
	"DNAExtractionProtocol": DNAExtractionProtocol,
	"Evaluation": Evaluation,
	"FluorescentMicroscopyMeasurement": FluorescentMicroscopyMeasurement,
	"FMRIMeasurement": FMRIMeasurement,
	"FMRIScannerSetup": FMRIScannerSetup,
	"ForcedSwimTestMeasurement": ForcedSwimTestMeasurement,
	"OpenFieldTestMeasurement": OpenFieldTestMeasurement,
	"Genotype": Genotype,
	"HandlingHabituationProtocol": HandlingHabituationProtocol,
	"HandlingHabituation": HandlingHabituation,
	"Ingredient": Ingredient,
	"Irregularity": Irregularity,
	"Incubation": Incubation,
	"LaserStimulationProtocol": LaserStimulationProtocol,
	"MeasurementUnit": MeasurementUnit,
	"Measurement": Measurement,
	"Observation": Observation,
	"Operator": Operator,
	"Operation": Operation,
	"OpticFiberImplant":OpticFiberImplant,
	"OpticFiberImplantProtocol":OpticFiberImplantProtocol,
	"OrthogonalStereotacticTarget": OrthogonalStereotacticTarget,
	"Protocol": Protocol,
	"SectioningProtocol": SectioningProtocol,
	"Substance": Substance,
	"SucrosePreferenceMeasurement": SucrosePreferenceMeasurement,
	"Solution": Solution,
	"Treatment": Treatment,
	"TreatmentProtocol": TreatmentProtocol,
	"Virus": Virus,
	"VirusInjectionProtocol": VirusInjectionProtocol,
	"WeightMeasurement": WeightMeasurement,
	}

def get_related_id(session, engine, parameters):
	category = parameters.split(":",1)[0]
	sql_query=session.query(ALLOWED_CLASSES[category])
	for field_value in parameters.split(":",1)[1].split("&&"):
		field, value = field_value.split(".",1)
		if ":" in value:
			values = get_related_id(session, engine, value)
			for value in values:
				value=int(value) # the value is returned as a numpy object
				if field[-4:] == "date": # support for date entry matching (the values have to be passes as string but matched as datetime)
					value = datetime.datetime(*[int(i) for i in value.split(",")])
				sql_query = sql_query.filter(getattr(ALLOWED_CLASSES[category], field)==value)
		else:
			if field[-4:] == "date": # support for date entry matching (the values have to be passes as string but matched as datetime)
				value = datetime.datetime(*[int(i) for i in value.split(",")])
			sql_query = sql_query.filter(getattr(ALLOWED_CLASSES[category], field)==value)
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

@argh.arg('-p', '--db_path', type=str)
@argh.arg('database', default=None, nargs="?")
def animal_info(identifier, database,
	db_path=None,
	):
	"""Return the __str__ attribute of an Animal object query filterd by the id column OR by arguments of the external_id objects.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	identifier : int or string
	The identifier of the animal

	database : string or None, optional
	If specified gives a constraint on the AnimalExternalIdentifier.database column AND truns the identifier attribute into a constraint on the AnimalExternalIdentifier.identifier column. If unspecified, the identfier argument is used as a constraint on the Animal.id column.
	"""

	if database and identifier:
		session, engine = load_session(db_path)
		sql_query = session.query(Animal)
		sql_query = sql_query.join(Animal.external_ids)\
		.filter(AnimalExternalIdentifier.database == database).filter(AnimalExternalIdentifier.identifier == identifier)\
		.options(contains_eager('external_ids'))
		identifier = [i for i in sql_query][0].id
		session.close()
		engine.dispose()

	session, engine = load_session(db_path)
	sql_query = session.query(Animal)
	sql_query = sql_query.filter(Animal.id == identifier)
	try:
		animal = [i.__str__() for i in sql_query][0]
	except:
		if database == None:
			print("No entry was found with {id} in the Animal.id column of the database located at {loc}.".format(id=identifier,loc=db_path))
		else:
			print("No entry was found with {id} in the AnimalExternalIdentifier.identifier column and {db} in the AnimalExternalIdentifier.database column of the database located at {loc}.".format(id=identifier,db=database,loc=db_path))
	else:
		print(animal)
	session.close()
	engine.dispose()

def cage_info(db_path, identifier,
	):
	"""Return the __str__ attribute of an Animal object query filterd by the id column OR by arguments of the external_id objects.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	identifier : int or string
	The identifier of the animal

	database : string or None, optional
	If specified gives a constraint on the AnimalExternalIdentifier.database colun AND truns the identifier attribute into a constraint on the AnimalExternalIdentifier.identifier column. If unspecified, the identfier argument is used as a constraint on the Animal.id column.
	"""

	session, engine = load_session(db_path)
	sql_query = session.query(Cage)
	sql_query = sql_query.filter(Cage.id == identifier)
	cage = [i.__str__() for i in sql_query][0]
	try:
		cage = [i.__str__() for i in sql_query][0]
	except:
		print("No entry was found with {id} in the Cage.id column of the database located at {loc}.".format(id=identifier,loc=db_path))
	else:
		print(cage)
	session.close()
	engine.dispose()

def load_session(db_path):
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
	joinclassobject = ALLOWED_CLASSES[class_name]

	#we need to catch this esception, because for aliased classes a mapper is not directly returned
	try:
		col_name_cols = inspection.inspect(joinclassobject).columns.items()
	except AttributeError:
		col_name_cols = inspection.inspect(joinclassobject).mapper.columns.items()

	for col_name, col in col_name_cols:
		column = getattr(joinclassobject, col.key)
		cols.append(column.label("{}_{}".format(class_name, col_name)))

def get_for_protocolize(db_path, class_name, code):
	"""Return a dataframe containing a specific entry from a given class name, joined with its related tables up to three levels down.
	"""
	session, engine = load_session(db_path)
	cols = []
	joins = []
	classobject = ALLOWED_CLASSES[class_name]
	insp = inspection.inspect(classobject)
	for name, col in insp.columns.items():
		cols.append(col.label(name))
	for name, rel in insp.relationships.items():
		alias = aliased(rel.mapper.class_, name=name)
		joins.append((alias, rel.class_attribute))
		for col_name, col in inspection.inspect(rel.mapper).columns.items():
			#the id column causes double entries, as it is mapped once on the parent table (related_table_id) and once on the child table (table_id)
			if col.key != "id":
				aliased_col = getattr(alias, col.key)
				cols.append(aliased_col.label("{}_{}".format(name, col_name)))

		sub_insp = inspection.inspect(rel.mapper.class_)
		for sub_name, sub_rel in sub_insp.relationships.items():
			if "contains" not in sub_name:
				sub_alias = aliased(sub_rel.mapper.class_, name=name+"_"+sub_name)
				joins.append((sub_alias, sub_rel.class_attribute))
				for sub_col_name, sub_col in inspection.inspect(sub_rel.mapper).columns.items():
					#the id column causes double entries, as it is mapped once on the parent table (related_table_id) and once on the child table (table_id)
					if sub_col.key != "id":
						sub_aliased_col = getattr(sub_alias, sub_col.key)
						cols.append(sub_aliased_col.label("{}_{}_{}".format(name, sub_name, sub_col_name)))

	sql_query = session.query(*cols).select_from(classobject)
	for join in joins:
		sql_query = sql_query.outerjoin(*join)
	sql_query = sql_query.filter(classobject.code == code)

	mystring = sql_query.statement
	mydf = pd.read_sql_query(mystring,engine)

	return mydf

def get_df(db_path,
	col_entries=[],
	default_join="inner",
	filters=[],
	join_entries=[],
	join_types=[],
	):
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
	!!!incomplete documentation


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

	session, engine = load_session(db_path)

	cols=[]
	for col_entry in col_entries:
		if len(col_entry) == 1:
			add_all_columns(cols, col_entry[0])
		if len(col_entry) == 2:
			cols.append(getattr(ALLOWED_CLASSES[col_entry[0]],col_entry[1]).label("{}_{}".format(*col_entry)))
		if len(col_entry) == 3:
			aliased_class = aliased(ALLOWED_CLASSES[col_entry[1]])
			ALLOWED_CLASSES[col_entry[0]+"_"+col_entry[1]] = aliased_class
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
				join_parameters.append(getattr(ALLOWED_CLASSES[class_name],table_name))
			else:
				join_parameters.append(ALLOWED_CLASSES[join_entry_substring])
		joins.append(join_parameters)

	sql_query = session.query(*cols)
	while len(join_types) < len(joins):
		if default_join == "outer":
			join_types.append("outer")
		elif default_join == "inner":
			join_types.append("inner")
	for ix, join in enumerate(joins):
		if join_types[ix] == "inner":
			sql_query = sql_query.join(*join)
		elif join_types[ix] == "outer":
			sql_query = sql_query.outerjoin(*join)

	for sub_filter in filters:
		if sub_filter:
			if sub_filter[1][-4:] == "date" and isinstance(sub_filter[2], str):
				for ix, i in enumerate(sub_filter[2:]):
					sub_filter[2+ix] = datetime.datetime(*[int(a) for a in i.split(",")])
			if len(sub_filter) == 3:
				sql_query = sql_query.filter(getattr(ALLOWED_CLASSES[sub_filter[0]], sub_filter[1]) == sub_filter[2])
			else:
				sql_query = sql_query.filter(or_(getattr(ALLOWED_CLASSES[sub_filter[0]], sub_filter[1]) == v for v in sub_filter[2:]))

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
