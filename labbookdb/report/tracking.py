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
	functional_scan_df = data_selection(db_path, "animals measurements")
	nonresponder_df = data_selection(db_path, "animals measurements irregularities")

	aggregation_dict = {
		'Animal_death_date' : lambda x: ', '.join(set([str(i) for i in x])),
		'Genotype_code' : lambda x: ', '.join(set(x)),
		}
	collapse_stuimulations = {
		'LaserStimulationProtocol_code' : lambda x: 0 if list(x) == [] else 1,
		"Animal_id" : lambda x: list(x)[0],
		}
	count_scans = {
		'occurences' : lambda x: sum(x),
		}
	collapse_nonresponders = {
		'Irregularity_description' : lambda x: 1 if "ICA failed to indicate response to stimulus" in list(x) else 0,
		"Animal_id" : lambda x: list(x)[0],
		}

	functional_scan_df = functional_scan_df.groupby('Measurement_id').agg(collapse_stuimulations)
	functional_scan_df = functional_scan_df.rename(columns={'LaserStimulationProtocol_code': 'occurences'})
	functional_scan_df = functional_scan_df.groupby('Animal_id').agg(count_scans)

	nonresponder_df = nonresponder_df.groupby('Measurement_id').agg(collapse_nonresponders)
	nonresponder_df = nonresponder_df.rename(columns={'Irregularity_description': 'occurences'})
	nonresponder_df = nonresponder_df.groupby('Animal_id').agg(count_scans)

	df = df.rename(columns={'AnimalExternalIdentifier_animal_id': 'Animal_id'})
	df = df.set_index(['Animal_id', 'AnimalExternalIdentifier_database'])['AnimalExternalIdentifier_identifier'].unstack(1).join(df.groupby('Animal_id').agg(aggregation_dict)).reset_index()
	df.set_index('Animal_id', inplace=True)
	df['nonresponsive'] = nonresponder_df
	df['functional'] = functional_scan_df
	df[['nonresponsive', 'functional']] = df[["nonresponsive", 'functional']].fillna(0).astype(int)
	df["responsive functional meausrements"] = df['functional'] - df['nonresponsive']
	df["responsive functional meausrements"] = df["responsive functional meausrements"].astype(str) +"/"+ df['functional'].astype(str)
	df.drop(['nonresponsive', 'functional'], axis = 1, inplace = True, errors = 'ignore')
	df = df.sort_index(ascending=False)

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

	if not skipped_cages:
		skipped_cages = ["None"]

	print("Next open cage number: {0}\nSkipped cage numbers: {1}".format(next_cage, ", ".join([str(i) for i in skipped_cages])))
	return
