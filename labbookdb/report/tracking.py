import os
import pandas as pd

import selection

try:
	from .db import query
except ValueError:
	import sys
	sys.path.append('/home/chymera/src/LabbookDB/labbookdb/db/')
	import query

def animal_id_table(db_path,
	save_as=None,
	):
	"""
	Return the list of animals and the
	"""
	df = selection.data_selection(db_path, "animal ids")
	df = df.sort_values('Animal_death_date', ascending=False)
	df.Animal_death_date = df.groupby('AnimalExternalIdentifier_animal_id', sort=False)['Animal_death_date'].ffill()
	df = df.set_index(['Animal_death_date','AnimalExternalIdentifier_animal_id', 'AnimalExternalIdentifier_database'])['AnimalExternalIdentifier_identifier'].unstack().reset_index()
	df.set_index('AnimalExternalIdentifier_animal_id', inplace=True)
	df = df.rename_axis(None, axis=1)
	df = df.sort_index(ascending=False)

	# piv = df.pivot_table(index=['AnimalExternalIdentifier_animal_id'], columns=['AnimalExternalIdentifier_database'])
	# print(piv.columns)
	# piv = piv['AnimalExternalIdentifier_identifier']
	# piv.join(df.groupby('AnimalExternalIdentifier_animal_id')['Animal_death_date'].first()).reset_index().rename_axis([None], axis=1)
	# print(piv)

	if save_as:
		df.to_html(os.path.abspath(os.path.expanduser(save_as)), col_space=300)
	else:
		print(df)
		print(df.columns)

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
