#!/usr/bin/python

import datetime
import argh
import json

from sqlalchemy import create_engine, literal
from os import path
from common_classes import *
from sqlalchemy.orm import sessionmaker

allowed_classes = {"animal": Animal, "cage": Cage, "substance": Substance, "solution": Solution}

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

def add_generic(db_path, category, parameters=""):

	category_class = allowed_classes[category]

	if not parameters:
		attributes = dir(category_class())
		filtered_attributes = [i for i in attributes if i[0] != "_"]
		message = "You can list the following keys as part of your parameters: " + ", ".join(filtered_attributes)
		return message

	parameters = json.loads(parameters)

	myobject = category_class()
	for key in parameters:
		setattr(myobject, key, parameters[key])

	add_to_db(db_path, myobject)


def commit_and_close(session, engine):
	session.commit()
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

argh.dispatch_command(add_generic)

if __name__ == '__main__':
	add_generic("~/meta.db", "animal")
	# add_animal("~/animal.db", 4011, 4, "f", "2L", id_uzh="M2760", cage_uzh="570971")
