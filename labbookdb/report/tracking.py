import os
import pandas as pd

try:
	from selection import data_selection
except ImportError:
	from .selection import data_selection

try:
	from ..db import query
except (ValueError, SystemError):
	import sys
	sys.path.append('/home/chymera/src/LabbookDB/labbookdb/db/')
	import query

TABLE_COL_SPACE = 200

def animals_id(db_path,
	save_as=None,
	):
	"""
	Extract list of animal (database and external) IDs, and either print it to screen or save it as an HTML file.

	Parameters
	----------

	db_path : string
	Path to the database file to query.

	save_as : string or None, optional
	Path under which to save the HTML report (".html" is automatically appended). If None, the report is printed to the terminal.
	"""

	df = data_selection(db_path, "animals id")

	df = df.rename(columns={'AnimalExternalIdentifier_database': 'External Database:', 'AnimalExternalIdentifier_animal_id': 'ID'})
	df = df.set_index(['ID', 'External Database:'])['AnimalExternalIdentifier_identifier'].unstack(1).reset_index()
	df.set_index('ID', inplace=True)
	df = df.sort_index(ascending=False)

	if save_as:
		df.to_html(os.path.abspath(os.path.expanduser(save_as+".html"), col_space=TABLE_COL_SPACE))
	else:
		print(df)
	return

def animals_info(db_path,
	save_as=None,
	):
	"""
	Extract list of animal (database and external) IDs and their death dates and genotypes, and either print it to screen or save it as an HTML file.

	Parameters
	----------

	db_path : string
	Path to the database file to query.

	save_as : string or None, optional
	Path under which to save the HTML report (".html" is automatically appended). If None, the report is printed to the terminal.
	"""

	df = data_selection(db_path, "animals info")

	aggregation_dict = {
		'Animal_death_date' : lambda x: ', '.join(set([str(i) for i in x])),
		'Genotype_code' : lambda x: ', '.join(set(x))
		}

	df = df.rename(columns={'AnimalExternalIdentifier_animal_id': 'ID'})
	print(df)
	return
	df = df.set_index(['ID', 'AnimalExternalIdentifier_database'])['AnimalExternalIdentifier_identifier'].unstack(1).join(df.groupby('ID').agg(aggregation_dict)).reset_index()
	df.set_index('ID', inplace=True)
	df = df.sort_index(ascending=False)

	return
	if save_as:
		df.to_html(os.path.abspath(os.path.expanduser(save_as+".html")), col_space=TABLE_COL_SPACE)
	else:
		print(df)
	return

def further_cages(db_path):
	"""
	Returns cage numbers that should be selected for incoming cages.

	Positional arguments:
	db_path -- path to database file to query (needs to be protocolizer-style)
	"""

	df = data_selection(db_path, "cage list")

	cages = df["Cage_id"].dropna().tolist()
	cages = list(set([int(i) for i in cages]))

	last_cage = cages[-1]
	next_cage = last_cage+1
	skipped_cages=[]
	for cage in cages:
		cage_increment = 1
		while True:
			if cage+cage_increment >= last_cage:
				break
			if cage+cage_increment not in cages:
				skipped_cages.append(cage+cage_increment)
				cage_increment += 1
			else:
				break

	return next_cage, skipped_cages

if __name__ == '__main__':
	animals_info("~/syncdata/meta.db")
