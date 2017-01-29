import os
import pandas as pd

import selection

try:
	from ..db import query
except ValueError:
	import sys
	sys.path.append('/home/chymera/src/LabbookDB/labbookdb/db/')
	import query

def animal_id_table(db_path,
	save_as=None,
	):
	"""
	Extract list of animal IDs and their death dates and eithe rprint it to screen or save it as an HTML file.

	Parameters
	----------

	db_path : string
	Path to the database file to query.

	save_as : string or None, optional
	Path under which to save the HTML report (".html" is automatically appended). If None, the report is printed to the terminal.
	"""

	df = selection.data_selection(db_path, "animal ids")

	df = df.set_index(['AnimalExternalIdentifier_animal_id', 'AnimalExternalIdentifier_database'])['AnimalExternalIdentifier_identifier'].unstack(1).join(df.groupby('AnimalExternalIdentifier_animal_id')['Animal_death_date'].first()).reset_index()
	df.set_index('AnimalExternalIdentifier_animal_id', inplace=True)
	df = df.sort_index(ascending=False)

	if save_as:
		df.to_html(os.path.abspath(os.path.expanduser(save_as+".html"), col_space=300))
	else:
		print(df)
		print(df.columns)
	return

def further_cages(db_path):
	"""
	Returns cage numbers that should be selected for incoming cages.

	Positional arguments:
	db_path -- path to database file to query (needs to be protocolizer-style)
	"""

	df = selection.data_selection(db_path, "cage list")

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
	print(further_cages("~/syncdata/meta.db"))
