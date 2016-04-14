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
	"SolutionAdministration": SolutionAdministration,
	}

def simple_query(db_path, category, field, value, mask="", first=True):
	session, engine = loadSession(db_path)
	sql_query=session.query(allowed_classes[category]).filter(getattr(allowed_classes[category], field)==value)
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
	simple_query("~/meta.db", "substance", "code", "flu", mask="id")
	# add_animal("~/animal.db", 4011, 4, "f", "2L", id_uzh="M2760", cage_uzh="570971")
