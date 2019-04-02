import pandas as pd
from labbookdb.db import query

def animal_id(db_path, database, identifier, reverse=False):
	"""Return the main LabbookDB animal identifier given an external database identifier.

	Parameters
	----------

	db_path : string
		Path to the database file to query.
	database : string
		Valid `AnimalExternalIdentifier.database` value.
	identifier : string
		Valid `AnimalExternalIdentifier.identifier` value.
	reverse : bool, optional
		Whether to reverse the query.
		A reverse query means that a LabbookDB `Animal.id` filter is applied and an `AnimalExternalIdentifier.identifier` value is returned.

	Returns
	-------
	int
		LabbookDB animal identifier.
	"""

	col_entries=[
		("Animal","id"),
		("AnimalExternalIdentifier",),
		]
	join_entries=[
		("Animal.external_ids",),
		]

	my_filters = []
	if reverse:
		my_filter = ["Animal","id",identifier]
		my_filters.append(my_filter)
	else:
		my_filter = ["AnimalExternalIdentifier","identifier",identifier]
		my_filters.append(my_filter)
	my_filter = ["AnimalExternalIdentifier","database",database]
	my_filters.append(my_filter)

	df = query.get_df(db_path,col_entries=col_entries, join_entries=join_entries, filters=my_filters)
	try:
		if reverse:
			labbookdb_id = df['AnimalExternalIdentifier_identifier'].item()
		else:
			labbookdb_id = df['Animal_id'].item()
	except ValueError as e:
		print('This may be happening because the identifier query value you have provided is of the wrong type (LabbookDB lookups are type-sensitive).')
		raise

	return labbookdb_id

def stimulation_protocol(db_path, code):
	"""Select a `pandas.DataFrame`object containing all events and associated measurement units for a specific stimulation protocol.

	Parameters
	----------

	db_path : string
		Path to the database file to query.

	code : string
		Code (valid `StimulationProtocol.code` value) which identifies the stimulation protocol to format.
	"""

	col_entries=[
		("StimulationProtocol",),
		("StimulationEvent",),
		("MeasurementUnit",),
		]
	join_entries=[
		("StimulationProtocol.events",),
		("StimulationEvent.unit",),
		]
	my_filters=[]
	my_filter = ["StimulationProtocol","code",code]
	my_filters.append(my_filter)

	df = query.get_df(db_path,col_entries=col_entries, join_entries=join_entries, filters=my_filters)

	return df

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

def animal_operations(db_path,
	animal_ids=[],
	implant_targets=[],
	virus_targets=[],
	):
	"""Select a dataframe of animals having been subjected to operative interventions with the given anatomical targets.

	Parameters
	----------

	db_path : str
	Path to a LabbookDB formatted database.

	animal_ids : list, optional
		A List of LabbookDB `Animal.id` values by which to filter the query.
		It is faster to filter using this mechanism than to return a dataframe for all animals and then filter that.

	implant_targets : list, optional
		A List of LabbookDB `OrthogonalStereotacticTarget.code` values which should be used to filter the query, while being joined to `Operation` objects via the `OpticFiberImplantProtocol` class.
		It is faster to filter using this mechanism than to return a dataframe for all animals and then filter that.

	virus_targets : list, optional
		A List of LabbookDB `OrthogonalStereotacticTarget.code` values which should be used to filter the query, while being joined to `Operation` objects via the `VirusInjectionProtocol` class.
		It is faster to filter using this mechanism than to return a dataframe for all animals and then filter that.

	Notes
	-----

	CAREFUL: Providing both `implant_targets` and `virus_targets` will return entries including only animals which have undergone an operation which has included protocols targeting both areas.
	If the areas were targeted by protocols included in different operations, the correspondence will not be detected.
	To obtain such a list please call the function twice and create a new dataframe from the intersection of the inputs on the `Animal_id` column.
	"""

	filters = []
	join_type = 'outer'
	col_entries=[
		("Animal","id"),
		("Operation",),
		("OpticFiberImplantProtocol",),
		("VirusInjectionProtocol",),
		("OrthogonalStereotacticTarget",),
		("Virus","OrthogonalStereotacticTarget",""),
		]
	join_entries=[
		("Animal.operations",),
		("OpticFiberImplantProtocol","Operation.protocols"),
		("VirusInjectionProtocol","Operation.protocols"),
		("OrthogonalStereotacticTarget","OpticFiberImplantProtocol.stereotactic_target"),
		("Virus_OrthogonalStereotacticTarget","VirusInjectionProtocol.stereotactic_target"),
		]
	my_filter=[]
	if animal_ids:
		my_filter = ["Animal","id"]
		my_filter.extend(animal_ids)
	if implant_targets:
		my_filter = ["OrthogonalStereotacticTarget","code"]
		my_filter.extend(implant_targets)
	if virus_targets:
		my_filter = ["Virus_OrthogonalStereotacticTarget","code"]
		my_filter.extend(virus_targets)
	filters.append(my_filter)

	df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=filters, default_join=join_type)

	return df


def animal_treatments(db_path,
	animal_ids=[],
	animal_treatments=[],
	cage_treatments=[],
	conjunctive=True,
	):
	"""Select a dataframe of animals and all treatments including animal-level or cage-level treatments.

	Parameters
	----------

	db_path : str
		Path to a LabbookDB formatted database.

	animal_ids : list, optional
		A List of LabbookDB `Animal.id` values by which to filter the query.
		It is faster to filter using this mechanism than to return a dataframe for all animals and then filter that.

	animal_treatments : list, optional
		A List of LabbookDB `Treatment.code` values which should be used to filter the query, while being joined to `Animal` objects.

	cage_treatments : list, optional
		A List of LabbookDB `Treatment.code` values which should be used to filter the query, while being joined to `Cage` objects - and further to `Animal` objects via `CageStay` objects.
		An onset check is also applied by the function, to ascertain that there is an overlap between the animal's presence in the cage and the cage treatment application.

	conjunctive : bool, optional
		Whether both `cage_treatments` and `animal_treatments` need to be satisfied (statements within each list are always disjunctive).

	Notes
	-----

	Currently `conjunctive=False` does not work; cage treatment and animal treatment filters are always conjunctive.
	"""

	filters = []
	join_type = 'outer'
	col_entries=[
		("Animal","id"),
		("Animal","death_date"),
		("Treatment",),
		("TreatmentProtocol","code"),
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
	my_filter=[]
	if animal_ids:
		my_filter = ["Animal","id"]
		my_filter.extend(animal_ids)
	if animal_treatments:
		my_filter = ["TreatmentProtocol","code"]
		my_filter.extend(animal_treatments)
	if cage_treatments:
		my_filter = ["Cage_TreatmentProtocol","code"]
		my_filter.extend(cage_treatments)
	filters.append(my_filter)

	df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=filters, default_join=join_type)

	# Generally dataframe operations should be performed in `labbookdb.report.tracking`, however, if animals are selected by cage treatment, we need to determine which animals actually received the treatment.
	# The following is therefore a selection issue.
	cage_treatment_columns = ['Cage_Treatment_id','Cage_Treatment_end_date','Cage_Treatment_start_date','Cage_TreatmentProtocol_code','Cage_Treatment_protocol_id']
	animals = list(df["Animal_id"].unique())
	cage_stays = cage_periods(db_path, animal_filter=animals)
	for subject in list(df['Animal_id'].unique()):
		for stay_start in df[df['Animal_id']==subject]['CageStay_start_date'].tolist():
			stay_end = cage_stays[(cage_stays['Animal_id']==subject)&(cage_stays['CageStay_start_date']==stay_start)]['CageStay_end_date'].tolist()[0]
			treatment_start = df[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start)]['Cage_Treatment_start_date'].tolist()[0]
			death_date = df[df['Animal_id']==subject]['Animal_death_date'].tolist()[0]
			# We do not check for treatment end dates, because often you may want to include recipients of incomplete treatments (e.g. due to death) when filtering based on cagestays.
			# Filtering based on death should be done elsewhere.
			if not pd.isnull(treatment_start):
				if not stay_start <= treatment_start and not treatment_start >= stay_end:
					df.loc[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start),cage_treatment_columns] = None
				elif treatment_start >= death_date:
					df.loc[(df['Animal_id']==subject)&(df['CageStay_start_date']==stay_start),cage_treatment_columns] = None
	df = df.drop_duplicates(subset=['Animal_id','Cage_id','Cage_Treatment_start_date', 'Cage_TreatmentProtocol_code', 'TreatmentProtocol_code'])

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


def cage_drinking_measurements(db_path,
	treatments=[]
	):
	""""""
	filters = []
	join_type = 'inner'
	col_entries=[
		("Cage","id"),
		("Treatment",),
		("TreatmentProtocol",'code'),
		('DrinkingMeasurement',)
		]
	join_entries=[
		("Cage.treatments",),
		("Treatment.protocol",),
		('DrinkingMeasurement',)
		]
	my_filter = []
	if treatments:
		my_filter = ["TreatmentProtocol","code"]
		my_filter.extend(treatments)
	filters.append(my_filter)

	df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=filters, default_join=join_type)

	return df


def animals_by_genotype(db_path, genotypes,
	attribute='code',
	):
	"""Return `pandas.Dataframe` object containing ID and genotype table columns of animals as matched by selected values on a selected Genotype attribute field.

	Parameters
	----------
	db_path : string
		Path to database file to query.
	genotypes : list
		List of strings containing values to be matched for the selected Genotype attribute.
	attribute : str
		Genotype attribute to match on.
	"""
	filters = []
	join_type = 'inner'
	col_entries=[
		("Animal","id"),
		("Genotype",),
		]
	join_entries=[
		("Animal.genotypes",),
		]
	my_filter = ["Genotype", attribute]
	my_filter.extend(genotypes)
	filters.append(my_filter)

	df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=filters, default_join=join_type)

	return df


def cage_periods(db_path,
	animal_filter=[],
	cage_filter=[],
	):
	"""
	Return a `pandas.DataFrame` object containing the periods which animals spent in which cages.

	Parameters
	----------
	db_path : string
		Path to database file to query.
	animal_filter : list, optional
		A list of `Animal.id` attribute values for which to specifically filter the query.

	Notes
	-----
	Operations on `pandas.DataFrame` objects should be performed in `labbookdb.report.tracking`, however, the cagestay end date is not explicitly recordes, so to select it or select animals by it, we calculate it here.
	"""
	df = parameterized(db_path, animal_filter=animal_filter, cage_filter=cage_filter, data_type='cage list')
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
	cage_filter=[],
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
		if animal_filter:
			my_filter = ['Animal','id']
			# for some reason this needs to be str
			my_filter.extend([str(i) for i in animal_filter])
	elif data_type == "animals measurements":
		col_entries=[
			("Animal","id"),
			("Measurement","id"),
			("StimulationProtocol","code"),
			]
		join_entries=[
			("Animal.measurements",),
			("FMRIMeasurement.stimulations",),
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
			# for some reason this needs to be str
			my_filter.extend([str(i) for i in animal_filter])
		if cage_filter:
			my_filter = ['Cage','id']
			# for some reason this needs to be str
			my_filter.extend([str(i) for i in cage_filter])
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
