import os
import pandas as pd
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
		'Genotype_code' : lambda x: ', '.join(set([str(i) for i in x])),
		}
	short_identifiers = make_identifier_short_form(df)
	df = short_identifiers.join(collapse_rename(df, 'AnimalExternalIdentifier_animal_id', collapse))
	df.reset_index().set_index('Animal_id', inplace=True)

	if functional_scan_responders:
		count_scans = {'occurences' : lambda x: sum(x),}

		collapse = {
			'StimulationProtocol_code' : lambda x: 0 if list(x) == [] else 1,
			"Animal_id" : lambda x: list(x)[0],
			}
		rename = {'StimulationProtocol_code': 'occurences'}
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
	return df

def bids_eventsfile(db_path, code,
	strict=False):
	"""
	Return a BIDS-formatted eventfile for a given code

	Parameters
	----------

	db_path : string
		Path to the database file to query.

	code : string
		Code (valid `StimulationProtocol.code` value) which identifies the stimulation protocol to format.
	strict : bool, optional
		Whether to strict about respecting BIDS specifics.
		(currently removes coumns with only empty cells)
	"""

	df = selection.stimulation_protocol(db_path, code)
	bids_df = pd.DataFrame([])
	bids_df['onset'] = df['StimulationEvent_onset']
	bids_df['duration'] = df['StimulationEvent_duration']
	bids_df['frequency'] = df['StimulationEvent_frequency']
	bids_df['pulse_width'] = df['StimulationEvent_pulse_width']
	bids_df['onset'] = df['StimulationEvent_onset']
	bids_df['trial_type'] = df['StimulationEvent_trial_type']
	bids_df['wavelength'] = df['StimulationEvent_wavelength']
	bids_df['strength'] = df['StimulationEvent_strength']
	bids_df['strength_unit'] = df['MeasurementUnit_code']

	if strict:
		bids_df = bids_df.dropna(axis=1, how='all')

	return bids_df

def cage_consumption(db_path, df,
	treatment_relative_date=True,
	rounding='D',
	):
	"""
	Return a `pandas.DataFrame` object containing information about the per-animal drinking solution consumption of single cages.

	Parameters
	----------
	db_path : string
		Path to the database file to query.
	df : pandas.DataFrame
		A `pandas.DataFrame` object with `DrinkingMeasurement_id`, `DrinkingMeasurement_reference_date`, `DrinkingMeasurement_date`, `DrinkingMeasurement_start_amount`, `DrinkingMeasurement_start_amount` columns.
		This can be obtained e.g. from `labbookdb.report.selection.cage_drinking_measurements()`.
	treatment_relative_date : bool, optional
		Whether to express the dates relative to a treatment onset.
		It is assumed that only one cage treatment is recorded per cage, if this is not so, this function may not work as expected.
	rounding : string, optional
		Whether to round dates and timedeltas - use strings as supported by pandas. [1]_

	Notes
	-----
	This function caluclates the per-day consumption based on phase-agnostic and potentially rounded and day values.
		This is prone to some inaccuracy, as drinking is generally restricted to specific times of the day.
		Ideally, a `waking_hour_consumption` should be estimated based on exact times of day and day cycle.

	References
	----------

	.. [1] http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
	"""

	selected_cages = list(df['Cage_id'].unique())
	occupancy_df = selection.cage_periods(db_path, cage_filter=selected_cages)
	df['occupancy']=''
	for measurement in df['DrinkingMeasurement_id'].tolist():
		selected = df[df['DrinkingMeasurement_id']==measurement]
		measurement_start = selected['DrinkingMeasurement_reference_date'].values[0]
		measurement_end = selected['DrinkingMeasurement_date'].values[0]
		cage_id = selected['Cage_id'].values[0]
		occupants = occupancy_df[
				(occupancy_df['CageStay_start_date']<=measurement_start)&
				(
					(occupancy_df['CageStay_end_date']>=measurement_end)|
					(occupancy_df['CageStay_end_date'].isnull())
				)&
				(occupancy_df['Cage_id']==cage_id)
				]
		if True in occupants['Animal_id'].duplicated().tolist():
			print(occupants)
			raise ValueError('An animal ist listed twice in the occupancy list of a cage (printed above). This biases the occupancy evaluation, and is likely diagnostic of a broader processing error.')
		occupancy = len(occupants.index)
		df.loc[(df['DrinkingMeasurement_id']==measurement),'occupancy'] = occupancy
	df['consumption'] = df['DrinkingMeasurement_start_amount']-df['DrinkingMeasurement_end_amount']
	if treatment_relative_date:
		df['relative_start_date'] = ''
		df['relative_end_date'] = ''
		df['relative_start_date'] = df['relative_start_date'].astype('timedelta64[ns]')
		df['relative_end_date'] = df['relative_end_date'].astype('timedelta64[ns]')
		df["relative_start_date"] = df["DrinkingMeasurement_reference_date"]-df["Treatment_start_date"]
		df["relative_end_date"] = df["DrinkingMeasurement_date"]-df["Treatment_start_date"]
		if rounding:
			df['relative_start_date'] = df['relative_start_date'].dt.round(rounding)
			df['relative_end_date'] = df['relative_end_date'].dt.round(rounding)
		df['relative_end_date'] = df['relative_end_date'].dt.days.astype(int)
		df['relative_start_date'] = df['relative_start_date'].dt.days.astype(int)

		# Here we calculate the day consumption based on phase-agnostic and potentially rounded and day values.
		# This is prone to some inaccuracy, as drinking is generally restricted to specific times of the day.
		# Ideally, a `waking_hour_consumption` should be estimated based on exact times of day and day cycle.
		df['day_consumption'] = df['consumption']/(df['relative_end_date'] - df['relative_start_date'])
		df['day_animal_consumption']=df['day_consumption']/df['occupancy']
	return df

def append_external_identifiers(db_path, df,
	concatenate=[],
	):
	"""
	Append external animal IDs to a dataframe containing an `Animal_id` (`Animal.id`) column.

	Parameters
	----------

	db_path : str
		Path to database fuile to query.
	df : pandas.DataFrame
		A `pandas.DataFrame` object containing an `Animal_id` (`Animal.id`) column.
	concatenate : list, optional
		A list containing any combination of 'Animal_death_date', 'Genotype_id', 'Genotype_code', 'Genotype_construct'.
	"""

	df_id = selection.parameterized(db_path, "animals info")

	collapse = {}
	if concatenate:
		for i in concatenate:
			collapse[i] = lambda x: ', '.join(set([str(i) for i in x]))
	short_identifiers = make_identifier_short_form(df_id)
	df_id = short_identifiers.join(collapse_rename(df_id, 'AnimalExternalIdentifier_animal_id', collapse))
	df_id.reset_index(inplace=True)
	df = pd.merge(df_id, df, on='Animal_id', how='inner')

	return df


def treatment_group(db_path, treatments,
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

	This function checks whether cage-level treatment onsets indeed happened during the period in which the animal was housed in teh cage.
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
		cage_stays = selection.cage_periods(db_path, animal_filter=animals)
		drop_idx = []
		for subject in list(df['Animal_id'].unique()):
			for stay_start in df[df['Animal_id']==subject]['CageStay_start_date'].tolist():
				stay_end = cage_stays[(cage_stays['Animal_id']==subject)&(cage_stays['CageStay_start_date']==stay_start)]['CageStay_end_date'].tolist()[0]
				treatment_start = df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)]['Cage_Treatment_start_date'].tolist()[0]
				death_date = df[df['Animal_id']==subject]['Animal_death_date'].tolist()[0]
				# We do not check for treatment end dates, because often you may want to include recipients of incomplete treatments (e.g. due to death) when filtering based on cagestays.
				# Filtering based on death should be done elsewhere.
				if not stay_start <= treatment_start and not treatment_start >= stay_end:
					drop_idx.extend(df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)].index.tolist())
				elif treatment_start >= death_date:
					drop_idx.extend(df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)].index.tolist())
		df = df.drop(drop_idx)
		df = df.drop_duplicates(subset=['Animal_id','Cage_id','Cage_Treatment_start_date', 'Cage_TreatmentProtocol_code'])
	return df

def qualitative_dates(df,
	iterator_column='Animal_id',
	date_column='relative_date',
	label='qualitative_date',
	fuzzy_matching={},
	):
	"""
	Assign qualitative date labels.

	Parameters
	----------

	df : pandas.DataFrame
		A `pandas.DataFrame` object containing a date column.
	iteraor_column : string, optional
		The label of the column which identifies the base entities of which each should be assigned a set of qualitatie dates (most commonly this is `Animal_id`, or `Cage_id`).
	date_column : string, optional
		The label of the column which serves as the quantitative record which is to be discretized into qualitative dates.
	label : string, optional
		The label to assign to the new qualitative date column.
	fuzzy_assignment : dict, optional
		A dictionary the keys of which are qualitative date labels to be assigned, and the values of which are lists giving the quantitative date labels in the order of preference based on which to assign the labels.
	"""

	df[label]=''
	for i in df[iterator_column]:
		try:
			for label, dates in fuzzy_matching.iteritems():
				for date in dates:
					if date in df[df[iterator_column]==i][date_column].values:
						df.loc[(df[iterator_column]==i)&(df[date_column]==date),'qualitative_date']=label
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
		onsets = treatment_group(db_path, list(reference.values())[0], level=list(reference.keys())[0])
		df['relative_date'] = ''
		df['relative_date'] = df['relative_date'].astype('timedelta64[ns]')
		for subject in df["Animal_id"]:
			try:
				df.loc[df["Animal_id"]==subject,"relative_date"] = df.loc[df["Animal_id"]==subject,"date"]-onsets.loc[onsets["Animal_id"]==subject, start_date_label].values[0]
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

def overview(db_path,
	default_join=False,
	filters=[],
	join_types=[],
	relative_dates=True,
	save_as="",
	rounding='D',
	rounding_type='round',
	):
	"""Returns an overview of events per animal.

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

	rounding_type : {'round','floor','ceil'}, optional
		Whether to round the dates (splits e.g. days apart at noon, hours at 30 minutes, etc.) or to take the floor or the ceiling.
	"""
	from behaviopy import plotting

	df = selection.timetable(db_path, filters, default_join, join_types=join_types)
	date_columns = ['Treatment_start_date', 'Treatment_end_date', 'FMRIMeasurement_date', 'OpenFieldTestMeasurement_date', 'ForcedSwimTestMeasurement_date', 'Cage_Treatment_start_date', 'Cage_Treatment_end_date',]

	if relative_dates:
		if isinstance(relative_dates, dict):
			df['reference_date'] = ''
			df['reference_date'] = df['reference_date'].astype('datetime64[ns]')
			reference_column = list(relative_dates.keys())[0]
			matching_column = list(list(relative_dates.values())[0].keys())[0]
			reference_matching = list(list(relative_dates.values())[0].values())[0]
			for subject in df['Animal_id'].unique():
				reference_date = df[(df['Animal_id']==subject)&(df[matching_column]==reference_matching)][reference_column].values[0]
				df.loc[df['Animal_id']==subject,'reference_date'] = reference_date
		elif isinstance(relative_dates, bool):
			df['reference_date'] = df['Cage_Treatment_start_date']
		elif "," in relative_dates or "-" in relative_dates:
			print('WARNING: The `relative_dates` value provided could be interpreted as a date. This feature is however not yet supported. Dates will be made relative to "Cage_Treatment_start_date" instead!')
			df['reference_date'] = df['Cage_Treatment_start_date']
		else:
			df['reference_date'] = df[relative_dates]
		for date_column in date_columns:
			try:
				df[date_column] = df[date_column]-df['reference_date']
			except TypeError:
				pass
			else:
				if rounding:
					if rounding_type == 'round':
						df[date_column] = df[date_column].dt.round(rounding)
					elif rounding_type == 'floor':
						df[date_column] = df[date_column].dt.floor(rounding)
					elif rounding_type == 'ceil':
						df[date_column] = df[date_column].dt.ceil(rounding)

	if save_as:
		save_as = os.path.abspath(os.path.expanduser(save_as))
		if not(save_as.endswith(".csv") or save_as.endswith(".CSV")):
			save_as += ".csv"
		df.to_csv(save_as)

	return df
