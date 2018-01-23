from .base_classes import *

cage_stay_association = Table('cage_stay_associations', Base.metadata,
	Column('cage_stays_id', Integer, ForeignKey('cage_stays.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
	)
genotype_association = Table('genotype_associations', Base.metadata,
	Column('genotypes_id', Integer, ForeignKey('genotypes.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
	)
ingredients_association = Table('ingredients_associations', Base.metadata,
	Column('solutions_id', Integer, ForeignKey('solutions.id')),
	Column('ingredients_id', Integer, ForeignKey('ingredients.id'))
	)
stimulation_events_association = Table('stimulation_events_associations', Base.metadata,
	Column('stimulation_events_id', Integer, ForeignKey('stimulation_events.id')),
	Column('stimulation_protocols_id', Integer, ForeignKey('stimulation_protocols.id'))
	)
stimulations_association = Table('stimulations_associations', Base.metadata,
	Column('fmri_measurements_id', Integer, ForeignKey('fmri_measurements.id')),
	Column('stimulation_protocols_id', Integer, ForeignKey('stimulation_protocols.id'))
	)
anesthesia_association = Table('anesthesia_associations', Base.metadata,
	Column('anesthesia_protocols_id', Integer, ForeignKey('anesthesia_protocols.id')),
	Column('treatment_protocols_id', Integer, ForeignKey('treatment_protocols.id'))
	)
operation_association = Table('operation_associations', Base.metadata,
	Column('operations_id', Integer, ForeignKey('operations.id')),
	Column('protocols_id', Integer, ForeignKey('protocols.id'))
	)
oprations_irregularities_association = Table('oprations_irregularities_association', Base.metadata,
	Column('operations_id', Integer, ForeignKey('operations.id')),
	Column('irregularities_id', Integer, ForeignKey('irregularities.id'))
	)
treatment_animal_association = Table('treatment_animal_associations', Base.metadata,
	Column('treatments_id', Integer, ForeignKey('treatments.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
	)
treatment_cage_association = Table('treatment_cage_associations', Base.metadata,
	Column('treatments_id', Integer, ForeignKey('treatments.id')),
	Column('cages_id', Integer, ForeignKey('cages.id'))
	)


#general classes:

class AnimalExternalIdentifier(Base):
	__tablename__ = "animal_external_identifiers"
	id = Column(Integer, primary_key=True)
	database = Column(String)
	identifier = Column(String)
	animal_id = Column(Integer, ForeignKey('animals.id'))

class Evaluation(Base):
	__tablename__ = "evaluations"
	id = Column(Integer, primary_key=True)

	path = Column(String) #path to file contining the data from evaluation
	author_id = Column(Integer, ForeignKey('operators.id'))
	author = relationship("Operator")

	measurement_id = Column(Integer, ForeignKey('measurements.id'))

class StimulationProtocol(Base):
	__tablename__ = "stimulation_protocols"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String, unique=True)
	#tme values specified in seconds, frequencies in hertz
	events = relationship("StimulationEvent", secondary=stimulation_events_association)

class Substance(Base):
	__tablename__ = "substances"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String, unique=True)
	long_name = Column(String, unique=True)
	concentration = Column(Float)
	concentration_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	concentration_unit = relationship("MeasurementUnit")
	supplier = Column(String)
	supplier_product_code = Column(String)
	pubchem_sid = Column(String)

class Ingredient(Base):
	__tablename__ = "ingredients"
	id = Column(Integer, primary_key=True)
	concentration = Column(Float)
	concentration_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	concentration_unit = relationship("MeasurementUnit")
	substance_id = Column(Integer, ForeignKey('substances.id'))
	substance = relationship("Substance")

class Solution(Base):
	__tablename__ = "solutions"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String, unique=True)
	supplier = Column(String)
	supplier_product_code = Column(String)
	contains = relationship("Ingredient", secondary=ingredients_association)

	def __repr__(self):
		return "<Solution(id='%s', code='%s', name='%s', contains='%s')>"\
		% (self.id, self.code, self.name, [str(self.contains[i].concentration)+" "+str(self.contains[i].concentration_unit.code)+" "+str(self.contains[i].substance.name) for i in range(len(self.contains))])


#behavioural classes:

class Arena(Base):
	__tablename__ = "arenas"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String, unique=True)
	shape = Column(String) # e.g. "square" or "round"
	x_dim = Column(Float) # in mm
	y_dim = Column(Float) # in mm
	z_dim = Column(Float) # in mm
	wall_color = Column(String)

	measurements = relationship("OpenFieldTestMeasurement")

class ForcedSwimTestMeasurement(Measurement):
	__tablename__ = 'forcedswimtest_measurements'
	__mapper_args__ = {'polymorphic_identity': 'forcedswimtest'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	temperature = Column(Float) #in degrees Centigrade
	data_path = Column(String) #path to the recording file
	evaluations = relationship("Evaluation")

	# Bracket of recording file representing this measurement:
	# Format: "x_start-x_end,y_start-y_end"
	# Values should be formatted as integers, and represent percent of the recording with and height
	recording_bracket = Column(String)

class OpenFieldTestMeasurement(Measurement):
	__tablename__ = 'openfieldtest_measurements'
	__mapper_args__ = {'polymorphic_identity': 'openfieldtest'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	center_luminostiy = Column(Integer) #in lux
	edge_luminostiy = Column(Integer) #in lux
	corner_luminostiy = Column(Integer) #in lux (only if `arena_shape == "square"`)
	data_path = Column(String) #path to the recording file

	arena_id = Column(Integer, ForeignKey('arenas.id'))
	evaluations = relationship("Evaluation")

class FMRIMeasurement(Measurement):
	__tablename__ = 'fmri_measurements'
	__mapper_args__ = {'polymorphic_identity': 'fmri'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	temperature = Column(Float)
	anesthesia_id = Column(Integer, ForeignKey('anesthesia_protocols.id'))
	anesthesia = relationship("AnesthesiaProtocol")
	scanner_setup_id = Column(Integer, ForeignKey('fmri_scanner_setups.id'))
	scanner_setup = relationship("FMRIScannerSetup")
	data_path = Column(String) #path to the recording file

	stimulations = relationship("StimulationProtocol", secondary=stimulations_association)

	def __str__(self):
		template = "fMRI({date}"
		if self.temperature:
			template += ': temp: {temp}'
		if self.stimulations:
			template +='; stim: {stimulations}'
		if any(["failed to indicate response to stimulus" in self.irregularities[i].description for i in range(len(self.irregularities))]):
			template += "; NONRESPONDENT"
		template += ")"
		return template.format(
			date=dt_format(self.date),
			temp=self.temperature,
			stimulations=", ".join([i.code for i in self.stimulations]),
			)

class AnesthesiaProtocol(Protocol):
	__tablename__ = 'anesthesia_protocols'
	__mapper_args__ = {'polymorphic_identity': 'anesthesia'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)

	bolus_to_maintenance_delay = Column(Float) #delay from start of bolus delivery to start of maintenance delivery, in seconds
	respiration = Column(String)

	induction = relationship("TreatmentProtocol", secondary=anesthesia_association)
	bolus = relationship("TreatmentProtocol", secondary=anesthesia_association)
	maintenance = relationship("TreatmentProtocol", secondary=anesthesia_association)
	recovery_bolus = relationship("TreatmentProtocol", secondary=anesthesia_association)

class VirusInjectionProtocol(Protocol):
	__tablename__ = 'virus_injection_protocols'
	__mapper_args__ = {'polymorphic_identity': 'virus_injection'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)
	amount = Column(Float) # injected virus amount, in microlitres
	virus_diffusion_time = Column(Float) # time to wait for virus to diffuse before retracting injector - in minutes
	virus_injection_speed = Column(Float) # speed at which the virus is injected - in nanolitres per minute

	stereotactic_target_id = Column(Integer, ForeignKey('orthogonal_stereotactic_targets.id'))
	stereotactic_target = relationship("OrthogonalStereotacticTarget", foreign_keys=[stereotactic_target_id])
	virus_id = Column(Integer, ForeignKey('viruses.id'))
	virus = relationship("Virus", foreign_keys=[virus_id])

class OpticFiberImplantProtocol(Protocol):
	__tablename__ = 'optic_fiber_implant_protocols'
	__mapper_args__ = {'polymorphic_identity': 'optic_fiber_implant'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)

	stereotactic_target_id = Column(Integer, ForeignKey('orthogonal_stereotactic_targets.id'))
	stereotactic_target = relationship("OrthogonalStereotacticTarget", foreign_keys=[stereotactic_target_id])
	optic_fiber_implant_id = Column(Integer, ForeignKey('implants.id'))
	optic_fiber_implant = relationship("OpticFiberImplant", foreign_keys=[optic_fiber_implant_id])


#treatment classes:

class HandlingHabituation(Base):
	__tablename__ = "handling_habituations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)

	cage_id = Column(Integer, ForeignKey('cages.id'))
	cage = relationship("Cage", back_populates="handling_habituations")

	protocol_id = Column(Integer, ForeignKey('handling_habituation_protocols.id'))
	protocol = relationship("HandlingHabituationProtocol")

class HandlingHabituationProtocol(Protocol):
	__tablename__ = 'handling_habituation_protocols'
	__mapper_args__ = {'polymorphic_identity': 'handling_habituation'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)
	session_duration = Column(Integer) #handling duration, per animal and per cage (assumed to be equal) in MINUTES
	individual_picking_up = Column(Boolean)
	group_picking_up = Column(Boolean)
	transparent_tube = Column(Boolean)

class Observation(Base):
	__tablename__ = "observations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	behaviour = Column(String)
	physiology = Column(String)
	severtity = Column(Integer, default=0)
	value = Column(Float)

	animal_id = Column(Integer, ForeignKey('animals.id'))
	unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	unit = relationship("MeasurementUnit")
	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")

class TreatmentProtocol(Protocol):
	__tablename__ = 'treatment_protocols'
	__mapper_args__ = {'polymorphic_identity': 'treatment'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)
	frequency = Column(String)
	route = Column(String)
	rate = Column(Float)
	rate_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	rate_unit = relationship("MeasurementUnit", foreign_keys=[rate_unit_id])
	dose = Column(Float)
	dose_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	dose_unit = relationship("MeasurementUnit", foreign_keys=[dose_unit_id])
	solution_id = Column(Integer, ForeignKey('solutions.id'))
	solution = relationship("Solution")

class DrinkingMeasurement(Measurement):
	__tablename__ = 'drinking_measurements'
	__mapper_args__ = {'polymorphic_identity': 'drinking'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	reference_date = Column(DateTime)
	#water consumption, in ml:
	consumption = Column(Float)
	#volumes in water source, in ml:
	start_amount = Column(Float)
	end_amount = Column(Float)

class SucrosePreferenceMeasurement(Measurement):
	__tablename__ = 'sucrosepreference_measurements'
	__mapper_args__ = {'polymorphic_identity': 'sucrosepreference'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	reference_date = Column(DateTime)
	#volumes in water source, in ml:
	water_start_amount = Column(Float)
	water_end_amount = Column(Float)
	sucrose_start_amount = Column(Float)
	sucrose_end_amount = Column(Float)
	sucrose_bottle_position = Column(String)
	sucrose_concentration = Column(Float)
	concentration_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	concentration_unit = relationship("MeasurementUnit")

class Treatment(Base):
	__tablename__ = "treatments"
	id = Column(Integer, primary_key=True)
	start_date = Column(DateTime) #date of first occurence
	end_date = Column(DateTime) #date of last occurence
	protocol_id = Column(Integer, ForeignKey('protocols.id'))
	protocol = relationship('Protocol')

	def __str__(self):
		return "protocol {protocol_code}, {start_date} - {end_date}"\
		.format(start_date=dt_format(self.start_date), end_date=dt_format(self.end_date), protocol_code=self.protocol.code)


#operation classes:

class Operation(Base):
	__tablename__ = "operations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)

	animal_id = Column(Integer, ForeignKey('animals.id'))

	irregularities = relationship("Irregularity", secondary=operations_irregularities_association)
	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")
	anesthesia_id = Column(Integer, ForeignKey('anesthesia_protocols.id'))
	anesthesia = relationship("AnesthesiaProtocol", foreign_keys=[anesthesia_id])
	protocols = relationship("Protocol", secondary=operation_association)
	irregularities = relationship("Irregularity", secondary=oprations_irregularities_association)

	def __str__(self):
		return "Operation({date}: {protocols})"\
		.format(date=dt_format(self.date), protocols="; ".join([i.type for i in self.protocols]))


#animal classes:

class Animal(Base):
	__tablename__ = "animals"
	id = Column(Integer, primary_key=True)
	birth_date = Column(DateTime)
	death_date = Column(DateTime)
	death_reason = Column(String)
	ear_punches = Column(String)
	license = Column(String)
	maximal_severtity = Column(Integer, default=0)
	sex = Column(String)

	cage_stays = relationship("CageStay", secondary=cage_stay_association, backref="animals")

	external_ids = relationship("AnimalExternalIdentifier")
	measurements = relationship("Measurement")

	genotypes = relationship("Genotype", secondary=genotype_association, backref="animals")
	treatments = relationship("Treatment", secondary=treatment_animal_association, backref="animals")

	observations = relationship("Observation")
	operations = relationship("Operation")

	biopsies = relationship("Biopsy", backref="animal")

	def __repr__(self):
		return "<Animal(id='%s', genotypes='%s', sex='%s', ear_punches='%s', treatment='%s')>"\
		% (self.id, [self.genotypes[i].construct+" "+self.genotypes[i].zygosity for i in range(len(self.genotypes))], self.sex, self.ear_punches,[self.treatments[i].protocol.solution for i in range(len(self.treatments))])
	def __str__(self):
		return "Animal(id: {id}, sex: {sex}, ear_punches: {ep}):\n"\
		"\tlicense:\t{license}\n"\
		"\tbirth:\t{bd}\n"\
		"\tdeath:\t{dd}\t(death_reason: {dr})\n"\
		"\texternal_ids:\t{eids}\n"\
		"\tgenotypes:\t{genotypes}\n"\
		"\tcage_stays:\t{cage_stays}\n"\
		"\toperations:\t{operations}\n"\
		"\ttreatments:\t{treatments}\n"\
		"\tmeasurements:\t{measurements}\n"\
		.format(id=self.id, sex=self.sex, ep=self.ear_punches,
		license=self.license,
		bd=dt_format(self.birth_date),
		dd=dt_format(self.death_date), dr=self.death_reason,
		eids=", ".join([self.external_ids[i].identifier+"("+self.external_ids[i].database+")" for i in range(len(self.external_ids))]),
		genotypes=", ".join([self.genotypes[i].construct+"("+self.genotypes[i].zygosity+")" for i in range(len(self.genotypes))]),
		operations="\n\t\t\t".join([self.operations[i].__str__() for i in range(len(self.operations))]),
		treatments="\n\t\t\t".join([self.treatments[i].__str__() for i in range(len(self.treatments))]),
		cage_stays="\n\t\t\t".join([self.cage_stays[i].__str__() for i in range(len(self.cage_stays))]),
		measurements="\n\t\t\t".join([self.measurements[i].__str__() for i in range(len(self.measurements))]),
		)

class CageStay(Base):
	__tablename__ = "cage_stays"
	id = Column(Integer, primary_key=True)

	start_date = Column(DateTime) #date of first occurence

	cage_id = Column(Integer, ForeignKey('cages.id'))
	cage = relationship("Cage", back_populates="stays")

	single_caged = Column(String) #if singel caged, state reason

	def __str__(self):
		return "cage {cage_id}, starting {start_date}"\
		.format(cage_id=self.cage_id, start_date=dt_format(self.start_date))
	def report_animals(self):
		return ["Animal "+str(i.id)+"["+", ".join([j.identifier+"("+j.database+")" for j in i.external_ids])+"] starting "+dt_format(self.start_date) for i in self.animals]

class Cage(Base):
	__tablename__ = "cages"
	id = Column(Integer, primary_key=True)

	handling_habituations = relationship("HandlingHabituation", back_populates="cage")
	treatments = relationship("Treatment", secondary=treatment_cage_association, backref="cages")
	measurements = relationship("Measurement")
	id_local = Column(String, unique=True)
	location = Column(String)
	environmental_enrichment = Column(String)
	stays = relationship("CageStay", back_populates="cage")

	def __str__(self):
		if self.id_local:
			idl = self.id_local
		else:
			idl = self.id
		return "Cage(id: {id}, location: {loc}, id_local: {idl}):\n"\
		"\t{stays}"\
		.format(id=self.id, idl=idl, loc=self.location, stays="\n\t".join(["\n\t".join(i.report_animals()) for i in self.stays]))

class WeightMeasurement(Measurement):
	__tablename__ = 'weight_measurements'
	__mapper_args__ = {'polymorphic_identity': 'weight'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	weight = Column(Float)
	weight_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	weight_unit = relationship("MeasurementUnit", foreign_keys=[weight_unit_id])

	def __str__(self):
		return "Weight({date}, weight: {w}{wu})"\
		.format(date=self.date, w=self.weight, wu=self.weight_unit.code)

class BrainBiopsy(Biopsy):
	__tablename__ = "brain_biopsies"
	__mapper_args__ = {'polymorphic_identity': 'brain'}
	id = Column(Integer, ForeignKey('biopsies.id'), primary_key=True)
	sectioning_protocol_id = Column(Integer, ForeignKey('protocols.id'))
	sectioning_protocol = relationship("Protocol", foreign_keys=[sectioning_protocol_id])


# DNA classes:

class Incubation(Base):
	__tablename__ = "incubations"
	id = Column(Integer, primary_key=True)
	revolutions_per_minute = Column(Float)
	duration = Column(Float)
	temperature = Column(Float)
	movement = Column(String) # "centrifuge" or "shake"

	duration_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	duration_unit = relationship("MeasurementUnit", foreign_keys=[duration_unit_id])
	#temperature - usually in degrees Centigrade
	temperature_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	temperature_unit = relationship("MeasurementUnit", foreign_keys=[temperature_unit_id])

class DNAExtraction(Base):
	__tablename__ = "dna_extractions"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	protocol_id = Column(Integer, ForeignKey('dna_extraction_protocols.id'))
	protocol = relationship('DNAExtractionProtocol')
	source_id = Column(Integer, ForeignKey('biopsies.id'))
	source = relationship('Biopsy')

class DNAExtractionProtocol(Protocol):
	__tablename__ = 'dna_extraction_protocols'
	__mapper_args__ = {'polymorphic_identity': 'dna_extraction'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)
	sample_mass = Column(Float)
	mass_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	mass_unit = relationship("MeasurementUnit", foreign_keys=[mass_unit_id])
	digestion_buffer_id = Column(Integer, ForeignKey("solutions.id"))
	digestion_buffer = relationship("Solution", foreign_keys=[digestion_buffer_id])
	digestion_buffer_volume = Column(Float)
	digestion_id = Column(Integer, ForeignKey("incubations.id"))
	digestion = relationship("Incubation", foreign_keys=[digestion_id])
	lysis_buffer_id = Column(Integer, ForeignKey("solutions.id"))
	lysis_buffer = relationship("Solution", foreign_keys=[lysis_buffer_id])
	lysis_buffer_volume = Column(Float)
	lysis_id = Column(Integer, ForeignKey("incubations.id"))
	lysis = relationship("Incubation", foreign_keys=[lysis_id])
	proteinase_id = Column(Integer, ForeignKey("solutions.id"))
	proteinase = relationship("Solution", foreign_keys=[proteinase_id])
	proteinase_volume = Column(Float)
	inactivation_id = Column(Integer, ForeignKey("incubations.id"))
	inactivation = relationship("Incubation", foreign_keys=[inactivation_id])
	cooling_id = Column(Integer, ForeignKey("incubations.id"))
	cooling = relationship("Incubation", foreign_keys=[cooling_id])
	centrifugation_id = Column(Integer, ForeignKey("incubations.id"))
	centrifugation = relationship("Incubation", foreign_keys=[centrifugation_id])

	volume_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	volume_unit = relationship("MeasurementUnit", foreign_keys=[volume_unit_id])

class BrainExtractionProtocol(Protocol):
	__tablename__ = 'brain_extraction_protocols'
	__mapper_args__ = {'polymorphic_identity': 'brain_extraction'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)
	perfusion_system = Column(String(50)) #e.g. "pump", "peristaltic pump", "syringe"
	perfusion_flow = Column(Float) #in ml/min
	peristaltic_frequency = Column(Float) #in Hz
	perfusion_solution_id = Column(Integer, ForeignKey("solutions.id"))
	perfusion_solution = relationship("Solution", foreign_keys=[perfusion_solution_id])
	perfusion_solution_volume = Column(Float) #in ml
	fixation_solution_id = Column(Integer, ForeignKey("solutions.id"))
	fixation_solution = relationship("Solution", foreign_keys=[fixation_solution_id])
	fixation_solution_volume = Column(Float) #in ml
	storage_solution_id = Column(Integer, ForeignKey("solutions.id"))
	storage_solution = relationship("Solution", foreign_keys=[storage_solution_id])
	storage_solution_volume = Column(Float) #in ml
	post_extraction_fixation_time = Column(Float) #in hours

class SectioningProtocol(Protocol):
	__tablename__ = 'sectioning_protocols'
	__mapper_args__ = {'polymorphic_identity': 'sectioning'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)
	system = Column(String(50)) #e.g. "vibratome", "cryotome", "microtome"
	slice_thickness = Column(Float) #in micrometres
	blade_frequency = Column(Float) #in Hz
	blade_speed = Column(Float) #in mm/s
	start_bregma_distance = Column(Float) #positive towards rostral, in mm
	start_interaural_distance = Column(Float) #positive towards rostral, in mm
	start_lambda_distance = Column(Float) #positive towards rostral, in mm
	start_midline_distance = Column(Float) #positive towards right of animal, in mm
	start_depth = Column(Float) #in mm


# Histological Classes

class FluorescentMicroscopyMeasurement(Measurement):
	__tablename__ = 'fluorescent_microscopy_measurements'
	__mapper_args__ = {'polymorphic_identity': 'fluorescent_microscopy'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	light_source = Column(String) # e.g. "LED", "LASER"
	stimulation_wavelength = Column(Float) #in nm
	imaged_wavelength = Column(Float) #in nm
	exposure = Column(Float) #in s
	data = Column(String) #path data folder
	biopsy_id = Column(Integer, ForeignKey('biopsies.id'))
