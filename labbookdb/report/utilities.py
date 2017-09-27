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
	df = df.set_index([index_name, 'AnimalExternalIdentifier_database'])['AnimalExternalIdentifier_identifier'].unstack(1)
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

