try:
	from ..db import query
except (ValueError, SystemError):
	from labbookdb.db import query

def animals_by_cage_treatment(db_path,
	codes=[],
	end_dates=[],
	start_dates=[],
	):
	"""Select a dataframe of animals and all related tables through to cage treatments based on cage_treatment filters.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	codes : list, optional
	Related TreatmentProtocol.code values based on which to filter dataframe

	end_dates : list, optional
	Related Treatment.end_date values based on which to filter dataframe

	start_dates : list, optional
	Related Treatment.start_date values based on which to filter dataframe
	"""

	col_entries=[
		("Animal","id"),
		("Cage","id"),
		("Treatment",),
		("TreatmentProtocol","code"),
		]
	join_entries=[
		("Animal.cage_stays",),
		("CageStay.cage",),
		("Cage.treatments",),
		("Treatment.protocol",),
		]
	my_filters=[]
	if codes:
		my_filter = ["TreatmentProtocol","code"]
		my_filter.extend(codes)
		my_filters.append(my_filter)
	if end_dates:
		my_filter = ["Treatment","end_date"]
		my_filter.extend(end_dates)
		my_filters.append(my_filter)
	if start_dates:
		my_filter = ["Treatment","start_date"]
		my_filter.extend(start_dates)
		my_filters.append(my_filter)
	if not my_filters:
		my_filters=[None]

	df = query.get_df(db_path,col_entries=col_entries, join_entries=join_entries, filters=my_filters)

	return df

def animals_by_treatment(db_path,
	codes=[],
	end_dates=[],
	start_dates=[],
	):
	"""Select a dataframe of animals and all related tables through to treatments based on treatment filters.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	codes : list, optional
	Related TreatmentProtocol.code values based on which to filter dataframe

	end_dates : list, optional
	Related Treatment.end_date values based on which to filter dataframe

	start_dates : list, optional
	Related Treatment.start_date values based on which to filter dataframe
	"""

	col_entries=[
		("Animal","id"),
		("Treatment",),
		("TreatmentProtocol","code"),
		]
	join_entries=[
		("Animal.treatments",),
		("Treatment.protocol",),
		]
	my_filters=[]
	if codes:
		my_filter = ["TreatmentProtocol","code"]
		my_filter.extend(codes)
		my_filters.append(my_filter)
	if end_dates:
		my_filter = ["Treatment","end_date"]
		my_filter.extend(end_dates)
		my_filters.append(my_filter)
	if start_dates:
		my_filter = ["Treatment","start_date"]
		my_filter.extend(start_dates)
		my_filters.append(my_filter)
	if not my_filters:
		my_filters=[None]

	df = query.get_df(db_path,col_entries=col_entries, join_entries=join_entries, filters=my_filters)

	return df

def by_animals(db_path, select, animals):
	"""Select a dataframe of animals and all related tables through to the "select" table based on animal filters.

	Parameters
	----------

	db_path : str
	Path to a LabbookDB formatted database.

	select : str
	For which kind of evaluation to select dataframe.

	animals : list of str
	Animal.id values based on which to filter dataframe
	"""

	accepted_select_values = ["sucrose preference","timetable"]

	if select == "sucrose preference":
		join_types = ["inner","inner","inner"]
		col_entries=[
			("Animal","id"),
			("Cage","id"),
			("SucrosePreferenceMeasurement",),
			]
		join_entries=[
			("Animal.cage_stays",),
			("CageStay.cage",),
			("SucrosePreferenceMeasurement",),
			]
	elif select == "timetable":
		col_entries=[
			("Animal","id"),
			("Treatment",),
			("FMRIMeasurement","date"),
			("OpenFieldTestMeasurement","date"),
			("ForcedSwimTestMeasurement","date"),
			("TreatmentProtocol","code"),
			("Cage","id"),
			("Cage","Treatment",""),
			("Cage","TreatmentProtocol","code"),
			("SucrosePreferenceMeasurement","date"),
			]
		join_entries=[
			("Animal.treatments",),
			("FMRIMeasurement",),
			("OpenFieldTestMeasurement","Animal.measurements"),
			("ForcedSwimTestMeasurement","Animal.measurements"),
			("Treatment.protocol",),
			("Animal.cage_stays",),
			("CageStay.cage",),
			("Cage_Treatment","Cage.treatments"),
			("Cage_TreatmentProtocol","Cage_Treatment.protocol"),
			("SucrosePreferenceMeasurement","Cage.measurements"),
			]
	else:
		raise ValueError("The value for select needs to be one of {}".format(accepted_select_values))

	animals = [str(i) for i in animals] #for some reason the Animal.id values need to be string :-/
	my_filter = ["Animal","id"]
	my_filter.extend(animals)

	df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=[my_filter], join_types=join_types)

	return df

def animal_treatments(db_path,
	cage_treatments=[],
	animal_treatments=[],
	conjunctive=True,
	):
	"""Select a dataframe of animals and all treatments including animal-level or cage-level treatments.

	Parameters
	----------

	db_path : str
	Path to a LabbookDB formatted database.

	select : str
	For which kind of evaluation to select dataframe.

	conjunctive : bool, optional
	Whether both `cage_treatments` and `animal_treatments` need to be satisfied (statements within each list are always disjunctive).

	Notes
	-----

	Currently `conjunctive=False` does not work; cage treatment and animal treatment filters are always conjunctive.
	"""

	filters = []
	join_type = 'outer'
	if animal_treatments:
		col_entries=[
			("Animal","id"),
			("Treatment",),
			("TreatmentProtocol","code"),
			]
		join_entries=[
			("Animal.treatments",),
			("Treatment.protocol",),
			]
		my_filter = ["TreatmentProtocol","code"]
		my_filter.extend(animal_treatments)
		filters.append(my_filter)
	elif cage_treatments:
		col_entries=[
			("Animal","id"),
			("CageStay","start_date"),
			("Cage","id"),
			("Cage","Treatment",""),
			("Cage","TreatmentProtocol","code"),
			]
		join_entries=[
			("Animal.treatments",),
			("Treatment.protocol",),
			("Animal.cage_stays",),
			("CageStay.cage",),
			("Cage_Treatment","Cage.treatments"),
			("Cage_TreatmentProtocol","Cage_Treatment.protocol"),
			]
		my_filter = ["Cage_TreatmentProtocol","code"]
		my_filter.extend(cage_treatments)
		filters.append(my_filter)
	else:
		raise ValueError("You must define at least one of the `cage_treatments` and `animal_treatments` parameters.")

	df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=filters, default_join=join_type)
	return df

def timetable(db_path, filters,
	default_join="outer",
	join_types=[],
	):
	"""Select a dataframe with animals as rown and all timetable-relevant events as columns.

	Parameters
	----------

	db_path : str
	Path to a LabbookDB formatted database.

	filters : list of list
	A list of lists giving filters for the query. It is passed to `..query.get_df()`.

	outerjoin_all : bool
	Pased as outerjoin_all to `..query.get_df()`
	"""

	col_entries=[
		("Animal","id"),
		("Treatment",),
		("FMRIMeasurement","date"),
		("OpenFieldTestMeasurement","date"),
		("ForcedSwimTestMeasurement","date"),
		("TreatmentProtocol","code"),
		("Cage","id"),
		("Cage","Treatment",""),
		("Cage","TreatmentProtocol","code"),
		("SucrosePreferenceMeasurement","date"),
		]
	join_entries=[
		("Animal.treatments",),
		("FMRIMeasurement",),
		("OpenFieldTestMeasurement","Animal.measurements"),
		("ForcedSwimTestMeasurement","Animal.measurements"),
		("Treatment.protocol",),
		("Animal.cage_stays",),
		("CageStay.cage",),
		("Cage_Treatment","Cage.treatments"),
		("Cage_TreatmentProtocol","Cage_Treatment.protocol"),
		("SucrosePreferenceMeasurement","Cage.measurements"),
		]

	# if treatment_start_dates:
	# 	my_filter = ["Treatment","start_date"]
	# 	my_filter.extend(treatment_start_dates)

	# setting outerjoin to true will indirectly include controls
	df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=filters, default_join=default_join, join_types=join_types)

	return df


def parameterized(db_path, data_type,
	animal_filter=[],
	treatment_start_dates=[],
	):
	"""Select dataframe from a LabbookDB style database.

	Parameters
	----------

	db_path : string
		Path to a LabbookDB formatted database.
	data_type : {"animals id", "animals info", "animals measurements", "animals measurements irregularities", "cage list", "forced swim"}
		What type of data should be selected values can be:
	animal_filter : list, optional
		A list of animal identifiers (`Animal.id` attributes) for which to limit the query.
	treatment_start_dates : list, optional
		A list containing the treatment start date or dates by which to filter the cages for the sucrose preference measurements.
		Items should be strings in datetime format, e.g. "2016,4,25,19,30".
	"""

	default_join = "inner"
	my_filter = []

	allowed_data_types = [
			"animals id",
			"animals info",
			"animals measurements",
			"animals measurements irregularities",
			"cage list",
			"forced swim",
			]

	if data_type == "animals id":
		col_entries=[
			("Animal","id"),
			("AnimalExternalIdentifier",),
			]
		join_entries=[
			("Animal.external_ids",),
			]
	elif data_type == "animals info":
		col_entries=[
			("Animal","death_date"),
			("AnimalExternalIdentifier",),
			("Genotype",),
			]
		join_entries=[
			("Animal.external_ids",),
			("Animal.genotypes",),
			]
	elif data_type == "animals measurements":
		col_entries=[
			("Animal","id"),
			("Measurement","id"),
			("LaserStimulationProtocol","code"),
			]
		join_entries=[
			("Animal.measurements",),
			("FMRIMeasurement.laser_stimulations",),
			]
	elif data_type == "animals measurements irregularities":
		col_entries=[
			("Animal","id"),
			("Measurement","id"),
			("Irregularity","description"),
			]
		join_entries=[
			("Animal.measurements",),
			("FMRIMeasurement.irregularities",),
			]
	elif data_type == "animals weights":
		col_entries=[
			("Animal","id"),
			("AnimalExternalIdentifier",),
			("WeightMeasurement",),
			]
		join_entries=[
			("Animal.external_ids",),
			("WeightMeasurement",),
			]
		my_filter = ["Measurement","type","weight"]
	elif data_type == "cage list":
		col_entries=[
			("Animal",),
			("CageStay",),
			("Cage","id"),
			]
		join_entries=[
			("Animal.cage_stays",),
			("CageStay.cage",),
			]
		if animal_filter:
			my_filter = ['Animal','id']
			my_filter.extend(animal_filter)
	elif data_type == "forced swim":
		col_entries=[
			("Animal","id"),
			("Cage","id"),
			("Treatment",),
			("TreatmentProtocol","code"),
			("ForcedSwimTestMeasurement",),
			("Evaluation",),
			]
		join_entries=[
			("Animal.cage_stays",),
			("ForcedSwimTestMeasurement",),
			("Evaluation",),
			("CageStay.cage",),
			("Cage.treatments",),
			("Treatment.protocol",),
			]
	else:
		raise ValueError("The `data_type` value needs to be one of: {}. You specified \"{}\"".format(", ".join(allowed_data_types), data_type))

	if treatment_start_dates:
		my_filter = ["Treatment","start_date"]
		my_filter.extend(treatment_start_dates)
	df = query.get_df(db_path,col_entries=col_entries, join_entries=join_entries, filters=[my_filter], default_join=default_join)

	return df
