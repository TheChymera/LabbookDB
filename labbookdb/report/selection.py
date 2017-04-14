try:
	from ..db import query
except (ValueError, SystemError):
	import sys
	sys.path.append('/home/chymera/src/LabbookDB/labbookdb/db/')
	import query

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

	accepted_select_values = ["sucrose preference"]

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
	else:
		raise ValueError("The value for select needs to be one of {}".format(accepted_select_values))

	animals = [str(i) for i in animals] #for some reason the Animal.id values need to be string :-/
	my_filter = ["Animal","id"]
	my_filter.extend(animals)

	df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=[my_filter], join_types=join_types)

	return df

def parameterized(db_path, data_type, treatment_start_dates=[]):
	"""Select dataframe from a LabbookDB style database.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	data_type : {"animals id", "animals info", "animals measurements", "animals measurements irregularities", "cage list", "forced swim"}
	What type of data should be selected values can be:

	treatment_start_dates : list, optional
	A list containing the treatment start date or dates by which to filter the cages for the sucrose preference measurements.
	Items should be strings in datetime format, e.g. "2016,4,25,19,30".
	"""

	elif data_type == "animals id":
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
	elif data_type == "cage list":
		col_entries=[
			("Animal","id"),
			("Cage","id"),
			]
		join_entries=[
			("Animal.cage_stays",),
			("CageStay.cage",),
			]
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

	if treatment_start_dates:
		my_filter = ["Treatment","start_date"]
		my_filter.extend(treatment_start_dates)
	else:
		my_filter = None
	df = query.get_df(db_path,col_entries=col_entries, join_entries=join_entries, filters=[my_filter])

	return df
