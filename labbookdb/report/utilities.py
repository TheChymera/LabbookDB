import pandas as pd

def concurrent_cagetreatment(df, cagestays,
	protect_duplicates=[
		'Animal_id',
		'Cage_id',
		'Cage_Treatment_start_date',
		'Cage_Treatment_end_date',
		'Cage_TreatmentProtocol_code',
		'Treatment_end_date',
		'Treatment_end_date',
		'TreatmentProtocol_code',
		],
	):
	"""
	Return a `pandas.DataFrame` object containing only `Cage_Treatment*` entries which are concurrent with the animal stay in the cage to which they were administered.

	Parameters
	----------

	df : pandas.DataFrame
		Pandas Dataframe, with columns containing:
			`Animal_id`,
			`Animal_death_date`,
			`CageStay_start_date`,
			`Cage_Treatment_start_date`,
			`Cage_TreatmentProtocol_code`.
	cagestays : pandas.DataFrame
		Pandas Dataframe, with columns containing:
			`Animal_id`,
			`CageStay_end_date`,
			`CageStay_start_date`,

	Notes
	-----

	This function checks whether cage-level treatment onsets indeed happened during the period in which the animal was housed in the cage.
	We do not check for the treatment end dates, as an animal which has received a partial treatment has received a treatment.
	Checks for treatment discontinuation due to e.g. death should be performed elsewhere.
	"""
	drop_idx = []
	for subject in list(df['Animal_id'].unique()):
		for stay_start in df[df['Animal_id']==subject]['CageStay_start_date'].tolist():
			stay_end = cagestays[(cagestays['Animal_id']==subject)&(cagestays['CageStay_start_date']==stay_start)]['CageStay_end_date'].tolist()[0]
			treatment_start = df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)]['Cage_Treatment_start_date'].tolist()[0]
			death_date = df[df['Animal_id']==subject]['Animal_death_date'].tolist()[0]
			# We do not check for treatment end dates, because often you may want to include recipients of incomplete treatments (e.g. due to death) when filtering based on cagestays.
			# Filtering based on death should be done elsewhere.
			if treatment_start <= stay_start or treatment_start >= stay_end:
				drop_idx.extend(df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)].index.tolist())
			elif treatment_start >= death_date:
				drop_idx.extend(df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)].index.tolist())
	df = df.drop(drop_idx)
	#df = df.drop_duplicates(subset=protect_duplicates)
	return df

def make_identifier_short_form(df,
	index_name="Animal_id"):
	"""
	Convert the long form `AnimalExternalIdentifier_identifier` column of a `pandas.DataFrame` to short-form identifier columns named after the corresponding values on the `AnimalExternalIdentifier_database` column.

	Parameters
	----------
	df : pandas.DataFrame
		A `pandas.DataFrame` object containing a long-form `AnimalExternalIdentifier_identifier` column and a dedicated `AnimalExternalIdentifier_database` column.
	index_name : str, optonal
		The name of a column from `df`, the values of which can be rendered unique. This column will serve as the index o the resulting dataframe.
	"""
	df = df.rename(columns={'AnimalExternalIdentifier_animal_id': 'Animal_id'})
	df = df.set_index([index_name, 'AnimalExternalIdentifier_database'])['AnimalExternalIdentifier_identifier']
	df = df.unstack(1)
	return df

def collapse_rename(df, groupby, collapse,
	rename=False,
	):
	"""
	Collapse long form columns according to a lambda function, so that groupby column values are rendered unique

	Parameters
	----------

	df : pandas.DataFrame
		A `pandas.DataFrame` object which you want to collapse.
	groupby : string
		The name of a column from `df`, the values of which you want to render unique.
	collapse : dict
		A dictionary the keys of which are columns you want to collapse, and the values of which are lambda functions instructing how to collapse (e.g. concatenate) the values.
	rename : dict, optional
		A dictionary the keys of which are names of columns from `df`, and the values of which are new names for these columns.
	"""
	df = df.groupby(groupby).agg(collapse)
	if rename:
		df = df.rename(columns=rename)

	return df

def relativize_dates(df,
	date_suffix='_date',
	rounding='D',
	rounding_type='round',
	reference_date=True,
	):
	"""
	Express dates on each row of a Pandas Dataframe as datetime objects relative to the row value on the 'reference_date' column.

	Parameters
	----------

	df : pandas.DataFrame
		Pandas Dataframe, with columns containing 'reference_date' and strings ending in `date_suffix`.
	date_suffix : str, optional
		String sufix via which to identify date columns needing manipulation.
	rounding : str, optional
		Datetime increment for date rounding.	
	rounding_type : {'round','floor','ceil'}, optional
		Whether to round the dates (splits e.g. days apart at noon, hours at 30 minutes, etc.) or to take the floor or the ceiling.
	"""

	if isinstance(reference_date, bool) and reference_date:
		df['reference_date'] = df['Cage_Treatment_start_date']
	elif isinstance(reference_date, str):
		df['reference_date'] = df[reference_date]
	date_columns = [i for i in df.columns.tolist() if i.endswith(date_suffix)]
	for date_column in date_columns:
		try:
			df[date_column] = df[date_column]-df['reference_date']
		except TypeError:
			pass
		else:
			if rounding:
				df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
				if rounding_type == 'round':
					df[date_column] = df[date_column].dt.round(rounding)
				elif rounding_type == 'floor':
					df[date_column] = df[date_column].dt.floor(rounding)
				elif rounding_type == 'ceil':
					df[date_column] = df[date_column].dt.ceil(rounding)
	return df
