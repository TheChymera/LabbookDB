import datetime

from sqlalchemy import create_engine, literal
from os import path
from common_classes import *
from sqlalchemy.orm import sessionmaker

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

def add_animal(db_path, id_eth, cage_eth, sex, ear_punches, id_uzh="", cahe_uzh=""):
	session, engine = loadSession(db_path)

	check_entry("id_eth", id_eth)
	if id_uzh:
		check_entry("id_uzh", id_uzh)

	new_genotype = Genotype(name=name, zygosity=zygosity)
	session.add(new_animal)
	commit_and_close(session, engine)

def commit_and_close(session, engine):
	session.commit()
	session.close()
	engine.dispose()

def check_entry(field, value):
	q=session.query(Animal).filter(getattr(Animal, field)==value)
	if session.query(literal(True)).filter(q.exists()).scalar():
		raise ValueError("Entry conflict for key "+field+" = "+value)


if __name__ == '__main__':
	Animal(id_eth=id_eth, cage_eth=cage_eth, sex=sex, ear_punches=ear_punches, id_uzh=id_uzh, cage_uzh=cage_uzh)
	add_animal("4011", "0004", "m", "2L", id_uzh="M2760", cage_uzh="570971")
