import pandas as pd
from sqlalchemy import create_engine, literal
from os import path
from common_classes import Animal, Genotype, Solution, ChronicTreatmentAdministration, ChronicTreatment, Weight, FMRIMeasurement, ChronicTreatment
from sqlalchemy.orm import sessionmaker

def next_cages_info(db_path, cage_code="cage_eth", return_skipped=True):
	"""
	Returns cage numbers that should be selected for incoming cages.

	Positional arguments:
	db_path -- path to database file to query (needs to be protocolizer-style)

	Keyword arguments:
	cage_code -- which cage entry to query (e.g. 'cage_eth' or 'cage_uzh')
	return_skipped -- also return skipped cage numbers (instead of just returning the next highest cage number)
	"""

	engine = initialize_read(db_path)
	session = load_session(engine)

	cage_code = "animals_"+cage_code

	sql_query = session.query(Animal).order_by(Animal.cage_eth)
	for item in sql_query:
		pass
	mystring = str(sql_query)
	mydf = pd.read_sql_query(mystring,engine)

	cage_selection = mydf[cage_code].dropna().tolist()
	existent_cages = set([int(cage) for cage in cage_selection])

	skipped_cages=[]
	for existent_cage in existent_cages:
		if existent_cage+1 not in existent_cages:
			skipped_cages.append(existent_cage+1)

	next_cage = skipped_cages[-1]
	if len(skipped_cages) > 1 and return_skipped:
		skipped_cages = skipped_cages[:-1]
		return next_cage, skipped_cages
	else:
		return next_cage

def load_session(engine):
	""""""
	Session = sessionmaker(bind=engine)
	session = Session()
	return session

def initialize_read(db_path):
	db_path = "sqlite:///" + path.expanduser(db_path)
	engine = create_engine(db_path, echo=False)
	return engine

#for testing purposes:
if __name__ == '__main__':
	print(next_cages_info("~/meta.db"))
