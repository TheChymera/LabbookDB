from sqlalchemy import create_engine, Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime, ForeignKeyConstraint, Boolean
from sqlalchemy.orm import backref, relationship, sessionmaker, validates
from os import path

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

genotype_association = Table('genotype_associations', Base.metadata,
	Column('genotypes_id', Integer, ForeignKey('genotypes.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)
treatment_animal_association = Table('treatment_animal_associations', Base.metadata,
	Column('treatments_id', Integer, ForeignKey('treatments.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)
treatment_cage_association = Table('treatment_cage_associations', Base.metadata,
	Column('treatments_id', Integer, ForeignKey('treatments.id')),
	Column('cages_id', Integer, ForeignKey('cages.id'))
)
operator_association = Table('operator_associations', Base.metadata,
	Column('operator_id', Integer, ForeignKey('operators.id')),
	Column('fmri_measurements_id', Integer, ForeignKey('fmri_measurements.id'))
)
ingredients_association = Table('ingredients_associations', Base.metadata,
	Column('solutions_id', Integer, ForeignKey('solutions.id')),
	Column('ingredients_id', Integer, ForeignKey('ingredients.id'))
)
laser_association = Table('laser_associations', Base.metadata,
	Column('laser_stimulation_protocols_id', Integer, ForeignKey('laser_stimulation_protocols.id')),
	Column('fmri_measurements_id', Integer, ForeignKey('fmri_measurements.id'))
)
irregularities_association = Table('irregularities_associations', Base.metadata,
	Column('fmri_measurements_id', Integer, ForeignKey('fmri_measurements.id')),
	Column('irregularities_id', Integer, ForeignKey('irregularities.id'))
)
authors_association = Table('authors_associations', Base.metadata,
	Column('protocols_id', Integer, ForeignKey('protocols.id')),
	Column('operators_id', Integer, ForeignKey('operators.id'))
)
cage_stay_association = Table('cage_stay_associations', Base.metadata,
	Column('cage_stays_id', Integer, ForeignKey('cage_stays.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)

#context-sensitive default functions
#(need to be functions taking only one input - http://docs.sqlalchemy.org/en/latest/core/defaults.html#context-sensitive-default-functions)
def mydefaultname(context):
	return context.current_parameters.get("name")

#meta classes:

class Protocol(Base):
	__tablename__ = "protocols"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String, unique=True)
	authors = relationship("Operator", secondary=authors_association)

	type = Column(String(50))
	__mapper_args__ = {
		'polymorphic_identity': 'protocol',
		'polymorphic_on': type
		}

class Measurement(Base):
	__tablename__ = "measurements"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)

	animal_id = Column(Integer, ForeignKey('animals.id')) # only set in per-animal measurements
	cage_id = Column(Integer, ForeignKey('cages.id')) # only set in per-cage measurements

	type = Column(String(50))
	__mapper_args__ = {
		'polymorphic_identity': 'measurement',
		'polymorphic_on': type
		}

#general classes:

class Operator(Base):
	__tablename__ = "operators"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	full_name = Column(String)
	affiliation = Column(String)
	email = Column(String)

	@validates('email')
	def validate_email(self, key, address):
		assert '@' in address
		return address

class MeasurementUnit(Base):
	__tablename__ = "measurement_units"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	long_name = Column(String)
	siunitx = Column(String)

class Substance(Base):
	__tablename__ = "substances"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String, unique=True)
	long_name = Column(String, unique=True, default=mydefaultname, onupdate=mydefaultname)
	concentration = Column(Float)
	concentration_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	concentration_unit = relationship("MeasurementUnit")
	supplier = Column(String)
	supplier_product_code = Column(String)


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

#fMRI classes:

class FMRIScannerSetup(Base):
	__tablename__ = "fmri_scanner_setups"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	coil = Column(String)
	scanner = Column(String)
	support = Column(String)

class FMRIMeasurement(Measurement):
	__tablename__ = 'fmri_measurements'
	__mapper_args__ = {'polymorphic_identity': 'fmri'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	temperature = Column(Float)
	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")
	preparation_id = Column(Integer, ForeignKey('fmri_animal_preparation_protocols.id'))
	preparation = relationship("FMRIAnimalPreparationProtocol")
	laser_stimulations = relationship("LaserStimulationProtocol", secondary=laser_association)
	scanner_setup_id = Column(Integer, ForeignKey('fmri_scanner_setups.id'))
	scanner_setup = relationship("FMRIScannerSetup")
	irregularities = relationship("Irregularity", secondary=irregularities_association)

class FMRIAnimalPreparationProtocol(Protocol):
	__tablename__ = 'fmri_animal_preparation_protocols'
	__mapper_args__ = {'polymorphic_identity': 'fmri_animal_preparation'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)
	induction_anesthesia_gas_id = Column(Integer, ForeignKey('treatment_protocols.id'))
	induction_anesthesia_gas = relationship("TreatmentProtocol", foreign_keys=[induction_anesthesia_gas_id])
	bolus_anesthesia_injection_id = Column(Integer, ForeignKey('treatment_protocols.id'))
	bolus_anesthesia_injection = relationship("TreatmentProtocol", foreign_keys=[bolus_anesthesia_injection_id])
	maintenance_anesthesia_gas_id = Column(Integer, ForeignKey('treatment_protocols.id'))
	maintenance_anesthesia_gas = relationship("TreatmentProtocol", foreign_keys=[maintenance_anesthesia_gas_id])
	maintenance_anesthesia_injection_id = Column(Integer, ForeignKey('treatment_protocols.id'))
	maintenance_anesthesia_injection = relationship("TreatmentProtocol", foreign_keys=[maintenance_anesthesia_injection_id])
	bolus_muscle_relaxant_injection_id = Column(Integer, ForeignKey('treatment_protocols.id'))
	bolus_muscle_relaxant_injection = relationship("TreatmentProtocol", foreign_keys=[bolus_muscle_relaxant_injection_id])
	maintenance_muscle_relaxant_injection_id = Column(Integer, ForeignKey('treatment_protocols.id'))
	maintenance_muscle_relaxant_injection = relationship("TreatmentProtocol", foreign_keys=[maintenance_muscle_relaxant_injection_id])

	respiration = Column(String)

class LaserStimulationProtocol(Base):
	__tablename__ = "laser_stimulation_protocols"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	#tme values specified in seconds, frequencies in hertz
	stimulus_repetitions = Column(Integer)
	stimulus_duration = Column(Float)
	inter_stimulus_duration = Column(Float)
	stimulation_onset = Column(Float)
	stimulus_frequency = Column(Float)
	pulse_width = Column(Float)

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

class Irregularity(Base):
	__tablename__ = "irregularities"
	id = Column(Integer, primary_key=True)
	description = Column(String, unique=True)

class Observation(Base):
	__tablename__ = "observations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	behaviour = Column(String)
	physiology = Column(String)
	severtity = Column(Integer, default=0)
	animal_id = Column(Integer, ForeignKey('animals.id'))

class UncategorizedTreatment(Base):
	__tablename__ = "uncategorized_treatment"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	description = Column(String)
	animal_id = Column(Integer, ForeignKey('animals.id'))

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
	protocol_id = Column(Integer, ForeignKey('treatment_protocols.id'))
	protocol = relationship('TreatmentProtocol')

#animal classes:

class Animal(Base):
	__tablename__ = "animals"
	id = Column(Integer, primary_key=True)
	id_eth = Column(Integer, unique=True)
	id_uzh = Column(String)
	sex = Column(String)
	ear_punches = Column(String)
	maximal_severtity = Column(Integer, default=0)

	birth_date = Column(DateTime)

	death_date = Column(DateTime)
	death_reason = Column(String)
	weights = relationship("Weight")

	cage_stays = relationship("CageStay", secondary=cage_stay_association)

	measurements = relationship("Measurement")

	genotypes = relationship("Genotype", secondary=genotype_association, backref="animals")
	treatments = relationship("Treatment", secondary=treatment_animal_association, backref="animals")

	observations = relationship("Observation")
	uncategorized_treatments = relationship("UncategorizedTreatment")

	def __repr__(self):
		return "<Animal(id='%s', id_eth='%s', id_uzh='%s', genotypes='%s', sex='%s', ear_punches='%s', treatment='%s')>"\
		% (self.id, self.id_eth, self.id_uzh, [self.genotypes[i].construct+" "+self.genotypes[i].zygosity for i in range(len(self.genotypes))], self.sex, self.ear_punches,[self.treatments[i].protocol.solution for i in range(len(self.treatments))])

class CageStay(Base):
	__tablename__ = "cage_stays"
	id = Column(Integer, primary_key=True)

	start_date = Column(DateTime) #date of first occurence
	end_date = Column(DateTime) #date of last occurence

	cage_id = Column(Integer, ForeignKey('cages.id'))
	cage = relationship("Cage", back_populates="stays")

	single_cged = Column(String) #if singel caged, state reason

class Cage(Base):
	__tablename__ = "cages"
	id = Column(Integer, primary_key=True)

	handling_habituations = relationship("HandlingHabituation", back_populates="cage")
	treatments = relationship("Treatment", secondary=treatment_cage_association, backref="cages")
	measurements = relationship("Measurement")
	id_local = Column(String, unique=True)
	location = Column(String)
	stays = relationship("CageStay", back_populates="cage")


class Genotype(Base):
	__tablename__ = "genotypes"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	construct = Column(String)
	zygosity = Column(String)

	def __repr__(self):
		return "<Genotype(code='%s', construct='%s' zygosity='%s')>"\
		% (self.code, self.construct, self.zygosity)

class Weight(Measurement):
	__tablename__ = 'Weight_measurements'
	__mapper_args__ = {'polymorphic_identity': 'Weight'}
	id = Column(Integer, ForeignKey('measurements.id'), primary_key=True)
	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")
	weight = Column(Float)
	weight_unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	weight_unit = relationship("MeasurementUnit", foreign_keys=[weight_unit_id])

class BioticSample(Base):
	__tablename__ = "biotic_samples"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	extracted = Column(DateTime)
	discriminator = Column('type', String(50))
	__mapper_args__ = {'polymorphic_on': discriminator}

class AnimalBiopsy(BioticSample):
	__tablename__ = "animal_biopsies"
	__mapper_args__ = {'polymorphic_identity': 'animal_biopsy'}
	id = Column(Integer, ForeignKey('biotic_samples.id'), primary_key=True)
	animal_id = Column(Integer, ForeignKey('animals.id'))
	animal = relationship("Animal")
	tissue = Column(String)

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
	source_id = Column(Integer, ForeignKey('biotic_samples.id'))
	source = relationship('BioticSample')

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
