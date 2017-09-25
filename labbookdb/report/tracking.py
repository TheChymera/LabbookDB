import os
from labbookdb.decorators import environment_db_path
from labbookdb.report.utilities import *
from labbookdb.report import selection
from labbookdb.db import query


TABLE_COL_SPACE = 150

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

	df = selection.parameterized(db_path, "animals id")

	df = df.rename(columns={'AnimalExternalIdentifier_database': 'External Database:', 'AnimalExternalIdentifier_animal_id': 'ID'})
	df = df.set_index(['ID', 'External Database:'])['AnimalExternalIdentifier_identifier'].unstack(1).reset_index()
	df.set_index('ID', inplace=True)
	df = df.sort_index(ascending=False)

	if save_as:
		df.to_html(os.path.abspath(os.path.expanduser(save_as+".html"), col_space=TABLE_COL_SPACE))
	else:
		print(df)
	return

@environment_db_path()
def animals_info(db_path,
	save_as=None,
	functional_scan_responders=True,
	treatments=True,
	):
	"""
	Extract list of animal (database and external) IDs and their death dates and genotypes, and either print it to screen or save it as an HTML file.

	Parameters
	----------

	db_path : string
		Path to the database file to query.

	save_as : string or None, optional
		Path under which to save the HTML report (".html" is automatically appended to the name, if not already present). If None, the report is printed to the terminal.

	functional_scan_responders : bool, optional
		Whether to create and list a column tracking how many of the scans in which an animal was exposed to stimulation show ICA results in a qualitative analysis.

	treatments : bool, optional
		Whether to create a and list columns tracking what animal-based and cage-based treatements the animal was subjected to.

	"""

	df = selection.parameterized(db_path, "animals info")

	collapse = {
		'Animal_death_date' : lambda x: ', '.join(set([str(i) for i in x])),
		'Genotype_code' : lambda x: ', '.join(set(x)),
		}
	short_identifiers = make_identifier_short_form(df)
	df = short_identifiers.join(collapse_rename(df, 'AnimalExternalIdentifier_animal_id', collapse))
	df.reset_index().set_index('Animal_id', inplace=True)

	if functional_scan_responders:
		count_scans = {'occurences' : lambda x: sum(x),}

		collapse = {
			'LaserStimulationProtocol_code' : lambda x: 0 if list(x) == [] else 1,
			"Animal_id" : lambda x: list(x)[0],
			}
		rename = {'LaserStimulationProtocol_code': 'occurences'}
		functional_scan_df = selection.parameterized(db_path, "animals measurements")
		functional_scan_df = collapse_rename(functional_scan_df, "Measurement_id", collapse, rename)
		functional_scan_df = collapse_rename(functional_scan_df, 'Animal_id', count_scans)

		collapse = {
			'Irregularity_description' : lambda x: 1 if "ICA failed to indicate response to stimulus" in list(x) else 0,
			"Animal_id" : lambda x: list(x)[0],
			}
		rename ={'Irregularity_description': 'occurences'}
		nonresponder_df = selection.parameterized(db_path, "animals measurements irregularities")
		nonresponder_df = collapse_rename(nonresponder_df, 'Measurement_id', collapse, rename)
		nonresponder_df = collapse_rename(nonresponder_df, 'Animal_id', count_scans)

		df['nonresponsive'] = nonresponder_df
		df['functional'] = functional_scan_df
		df[['nonresponsive', 'functional']] = df[["nonresponsive", 'functional']].fillna(0).astype(int)
		df["responsive functional scans"] = df['functional'] - df['nonresponsive']
		df["responsive functional scans"] = df["responsive functional scans"].astype(str) +"/"+ df['functional'].astype(str)
		df.drop(['nonresponsive', 'functional'], axis = 1, inplace = True, errors = 'ignore')

	if treatments:
		treatments_df = selection.animal_treatments(db_path)
		collapse_treatments = {
			'TreatmentProtocol_code' : lambda x: ', '.join(set([str(i) for i in x if i])),
			'Cage_TreatmentProtocol_code' : lambda x: ', '.join(set([i for i in x if i])),
			}
		treatments_rename = {
			'TreatmentProtocol_code': 'animal_treatment',
			'Cage_TreatmentProtocol_code': 'cage_treatment',
			}
		treatments_df = treatments_df.groupby('Animal_id').agg(collapse_treatments)
		treatments_df = treatments_df.rename(columns=treatments_rename)
		df['animal_treatment'] = treatments_df["animal_treatment"]
		df['cage_treatment'] = treatments_df["cage_treatment"]

	df = df.sort_index(ascending=False)
	df = df.fillna('')
	if save_as:
		if os.path.splitext(save_as)[1] in [".html",".HTML"]:
			df.to_html(os.path.abspath(os.path.expanduser(save_as)), col_space=TABLE_COL_SPACE)
		elif os.path.splitext(save_as)[1] in [".tsv",".TSV"]:
			df.to_csv(save_as, sep='\t', encoding='utf-8')
		elif os.path.splitext(save_as)[1] in [".csv",".CSV", ""]:
			df.to_csv(save_as, encoding='utf-8')
		else:
			print("WARNING: This function currently only supports `.csv`, `.tsv`, or `.html` output. Please append one of the aforementioned extensions to the specified file name (`{}`), or specify no extension - in which case `.csv` will be added and an according output will be created.".format(save_as))
	else:
		print(df)
	return

def cage_periods(db_path,
	animal_filter=[],
	):
	"""
	Return a `pandas.DataFrame` object containing the periods which animals spent in which cages.

	Parameters
	----------
	db_path : string
		Path to database file to query.
	animal_filter : list, optional
		A list of `Animal.id` attribute values for which to specifically filter the query.
	"""
	df = selection.parameterized(db_path, animal_filter=animal_filter, data_type='cage list')
	df['CageStay_end_date'] = ''
	for subject in df['Animal_id'].unique():
		for start_date in df[df['Animal_id']==subject]['CageStay_start_date'].tolist():
			possible_end_dates = df[(df['Animal_id']==subject)&(df['CageStay_start_date']>start_date)]['CageStay_start_date'].tolist()
			try:
				end_date = min(possible_end_dates)
			except ValueError:
				end_date = None
			if not end_date:
				end_date = df[df['Animal_id']==subject]['Animal_death_date'].tolist()[0]
			df.loc[(df['Animal_id']==subject)&(df['CageStay_start_date']==start_date),'CageStay_end_date'] = end_date
	return df

def treatment_onsets(db_path, treatments,
	level="",
	):
	"""
	Return a `pandas.DataFrame` object containing the per animal start dates of a particular treatment code (applied either at the animal or the cage levels).

	Parameters
	----------

	db_path : string
		Path to database file to query.
	code : string
		Desired treatment code (`Treatment.code` attribute) to filter for.
	level : {"animal", "cage"}
		Whether to query animal treatments or cage treatments.

	Notes
	-----

	This function checks whether cage-leve treatment onsets indeed happened during the period in which the animal was housed int eh cage.
	We do not check for the treatment end dates, as an animal which has received a partial treatment has received a treatment.
	Checks for treatment discontinuation due to e.g. death should be performed elsewhere.
	"""
	if not level:
		level = "animal"
	if level=="animal":
		df = selection.animal_treatments(db_path, animal_treatments=treatments)
	elif level=="cage":
		df = selection.animal_treatments(db_path, cage_treatments=treatments)
		animals = list(df["Animal_id"].unique())
		cage_stays = cage_periods(db_path, animal_filter=animals)
		drop_idx = []
		for subject in list(df['Animal_id'].unique())[-1:]:
			for stay_start in df[df['Animal_id']==subject]['CageStay_start_date'].tolist():
				stay_end = cage_stays[(cage_stays['Animal_id']==subject)&(cage_stays['CageStay_start_date']==stay_start)]['CageStay_end_date'].tolist()[0]
				treatment_start = df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)]['Cage_Treatment_start_date'].tolist()[0]
				# We do not check for treatment end dates, because often you may want to include recipients of incomplete treatments (e.g. due to death) when filtering based on cagestays.
				# Filtering based on death should be done elsewhere.
				if not stay_start <= treatment_start and not treatment_start >= stay_end:
					drop_idx.extend(df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)].index.tolist())
		df = df.drop(drop_idx)

	return df

def qualitative_dates(df,
	iterator_column='Animal_id',
	date_column='relative_date',
	fuzzy_matching={},
	):
	"""
	Assign qualitative date labels.

	Parameters
	----------

	df : pandas.DataFrame
		A `pandas.DataFrame` object containing a date column.
	fuzzy_assignment : dict, optional
		A dictionary the keys of which are qualitative date labels to be assigned, and the values of which are lists giving the quantitative date labels in the order of preference based on which to assign the labels.
	"""

	df['qualitative_date']=""
	for i in df[iterator_column]:
                try:
                        for label, dates in fuzzy_matching.iteritems():
                                for date in dates:
                                        if date in df[df[iterator_column]==i][date_column]:
                                                break
                except AttributeError:
                        for label, dates in fuzzy_matching.items():
                                for date in dates:
                                        if date in df[df[iterator_column]==i][date_column].values:
                                                df.loc[(df[iterator_column]==i)&(df[date_column]==date),'qualitative_date']=label
                                                break
	return df

def animal_weights(db_path,
	reference={},
	rounding="D",
	):
	"""
	Return a dataframe containing animal weights and dates.

	Parameters
	----------

	db_path : string
		Path to database file to query.
	reference : dict, optional
		Dictionary based on which to apply a reference date for the dates of each animal. Keys of this dictionary must be "animal" or "cage", and values must be lists of treatment codes.
	rounding : string, optional
		Whether to round dates and timedeltas - use strings as supported by pandas. [1]_

	References
	----------

	.. [1] http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
	"""
	import pandas as pd

	df = selection.parameterized(db_path, "animals weights")
	short_identifiers = make_identifier_short_form(df, index_name="WeightMeasurement_id")
	collapse = {
		'WeightMeasurement_date' : lambda x: list(set(x))[0] if (len(set(x)) == 1) else "WARNING: different values were present for this entry. Data in this entire DataFrame may not be trustworthy.",
		'WeightMeasurement_weight' : lambda x: list(set(x))[0] if (len(set(x)) == 1) else "WARNING: different values were present for this entry. Data in this entire DataFrame may not be trustworthy.",
		'AnimalExternalIdentifier_animal_id' : lambda x: list(set(x))[0] if (len(set(x)) == 1) else "WARNING: different values were present for this entry. Data in this entire DataFrame may not be trustworthy.",
		}
	rename = {
		'WeightMeasurement_date': 'date',
		'WeightMeasurement_weight': 'weight',
		'AnimalExternalIdentifier_animal_id': 'Animal_id',
		}
	df = short_identifiers.join(collapse_rename(df, 'WeightMeasurement_id', collapse, rename))
	if reference:
		if list(reference.keys())[0] == 'animal':
			start_date_label = 'Treatment_start_date'
		elif list(reference.keys())[0] == 'cage':
			start_date_label = 'Cage_Treatment_start_date'
		onsets = treatment_onsets(db_path, list(reference.values())[0], level=list(reference.keys())[0])
		df["relative_date"]=''
		for subject in df["Animal_id"]:
			try:
				df.loc[df["Animal_id"]==subject,"relative_date"] = df.loc[df["Animal_id"]==subject,"date"] - onsets.loc[onsets["Animal_id"]==subject, start_date_label].values[0]
			except IndexError:
				df.drop(df[df["Animal_id"]==subject].index, inplace=True)
		df = pd.merge(df, onsets, on='Animal_id', how='outer')
		if rounding:
			df['relative_date'] = df['relative_date'].dt.round(rounding)
	if rounding:
		df['date'] = df['date'].dt.round(rounding)

	return df

def further_cages(db_path):
	"""
	Returns cage numbers that should be selected for incoming cages.

	Parameters
	----------
		db_path : path to database file to query (needs to be protocolizer-style)
	"""

	df = selection.parameterized(db_path, "cage list")

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

def treatments_plot(db_path,
	default_join=False,
	draw=[],
	filters=[],
	join_types=[],
	real_dates=True,
	saturate=[],
	save_df="",
	save_plot="",
	shade=[],
	window_end="",
	):
	"""Plot a timetable of events per animal.

	Parameters
	----------

	db_path : string
	Path to the database file to query.

	outerjoin_all : bool
	Pased as outerjoin_all to `..query.get_df()`

	filters : list of list, optional
	A list of lists giving filters for the query. It is passed to ..query.get_df().

	saturate : {list of str, list of dict}, optional
	A list of dictionaries or strings specifying by which criteria to saturate cells. It is passed to behaviopy.timetable.multi_plot()

	save_df : string, optional
	Path under which to save the plotted dataframe. ".csv" will be appended to the string, and the data will be saved in CSV format.

	window_end : string
	A datetime-formatted string (e.g. "2016,12,18") to apply as the timetable end date (overrides autodetected end).
	"""
	from behaviopy import plotting

	df = selection.timetable(db_path, filters, default_join, join_types=join_types)

	if save_df:
		df_path = os.path.abspath(os.path.expanduser(save_df))
		if not(df_path.endswith(".csv") or df_path.endswith(".CSV")):
			df_path += ".csv"
		df.to_csv(df_path)

	plotting.timetable(df, "Animal_id",
		draw=draw,
		shade=shade,
		saturate=saturate,
		save_as=save_plot,
		window_end=window_end,
		real_dates=real_dates,
		)
