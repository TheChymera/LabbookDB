from sqlalchemy import create_engine, Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime, ForeignKeyConstraint, Boolean
from sqlalchemy.orm import backref, relationship, sessionmaker, validates
from os import path

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

genotype_association = Table('genotype_associations', Base.metadata,
	Column('genotypes_id', Integer, ForeignKey('genotypes.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)
treatment_association = Table('treatment_associations', Base.metadata,
	Column('chronic_treatments_id', Integer, ForeignKey('chronic_treatments.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)
solution_association = Table('solution_associations', Base.metadata,
	Column('soution_administrations_id', Integer, ForeignKey('solution_administrations.id')),
	Column('solutions_id', Integer, ForeignKey('solutions.id'))
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

#meta classes:

class Protocol(Base):
	__tablename__ = "protocols"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String, unique=True)
	authors = relationship("Operator", secondary=authors_association)

	discriminator = Column('type', String(50))
	__mapper_args__ = {'polymorphic_on': discriminator}

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
	name = Column(String)
	concentration = Column(Float)
	concentration_unit_id = Column(String, ForeignKey('measurement_units.id'))
	concentration_unit = relationship("MeasurementUnit")
	supplier = Column(String)
	supplier_product_code = Column(String)


class Ingredient(Base):
	__tablename__ = "ingredients"
	id = Column(Integer, primary_key=True)
	concentration = Column(Float)
	concentration_unit_id = Column(String, ForeignKey('measurement_units.id'))
	concentration_unit = relationship("MeasurementUnit")
	contained = Column(Integer, ForeignKey("ingredients.id"))
	substance_id = Column(Integer, ForeignKey('substances.id'))
	substance = relationship("Substance")

class Solution(Base):
	__tablename__ = "solutions"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String)
	supplier = Column(String)
	supplier_id = Column(String)
	contains = relationship("Ingredient", secondary=ingredients_association)

#fMRI classes:

class FMRIScannerSetup(Base):
	__tablename__ = "scanner_setups"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	coil = Column(String)
	support = Column(String)

class FMRIMeasurement(Base):
	__tablename__ = "fmri_measurements"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	temperature = Column(Float)
	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")
	preparation_id = Column(Integer, ForeignKey('fmri_animal_preparation_protocols.id'))
	preparation = relationship("FMRIAnimalPreparationProtocol")
	laser_stimulations = relationship("LaserStimulationProtocol", secondary=laser_association)
	scanner_setup_id = Column(Integer, ForeignKey('scanner_setups.id'))
	scanner_setup = relationship("FMRIScannerSetup")
	animal_id = Column(Integer, ForeignKey('animals.id'))
	irregularities = relationship("Irregularity", secondary=irregularities_association)

class FMRIAnimalPreparationProtocol(Protocol):
	__tablename__ = 'fmri_animal_preparation_protocols'
	__mapper_args__ = {'polymorphic_identity': 'fmri_animal_preparation'}
	id = Column(Integer, ForeignKey('protocols.id'), primary_key=True)
	induction_anesthesia_gas_id = Column(Integer, ForeignKey('solution_administrations.id'))
	induction_anesthesia_gas = relationship("SolutionAdministration", foreign_keys=[induction_anesthesia_gas_id])
	bolus_anesthesia_injection_id = Column(Integer, ForeignKey('solution_administrations.id'))
	bolus_anesthesia_injection = relationship("SolutionAdministration", foreign_keys=[bolus_anesthesia_injection_id])
	maintenance_anesthesia_gas_id = Column(Integer, ForeignKey('solution_administrations.id'))
	maintenance_anesthesia_gas = relationship("SolutionAdministration", foreign_keys=[maintenance_anesthesia_gas_id])
	maintenance_anesthesia_injection_id = Column(Integer, ForeignKey('solution_administrations.id'))
	maintenance_anesthesia_injection = relationship("SolutionAdministration", foreign_keys=[maintenance_anesthesia_injection_id])
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

	parent_id = Column(Integer, ForeignKey('parent.id'))

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
	description = Column(String)

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

class ChronicTreatmentAdministration(Base):
	__tablename__ = "chronic_treatment_administrations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	deviating_solution_amount = Column(Integer)
	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")
	treatment_id = Column(Integer, ForeignKey("chronic_treatments.id"))

class ChronicTreatment(Base):
	__tablename__ = "chronic_treatments"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	name = Column(String)
	frequency = Column(String)
	route = Column(String)
	rate = Column(Float)
	rate_unit_id = Column(String, ForeignKey('measurement_units.id'))
	rate_unit = relationship("MeasurementUnit", foreign_keys=[rate_unit_id])
	dose = Column(Float)
	dose_unit_id = Column(String, ForeignKey('measurement_units.id'))
	dose_unit = relationship("MeasurementUnit", foreign_keys=[dose_unit_id])
	administrations = relationship("ChronicTreatmentAdministration")

class SolutionAdministration(Base):
	__tablename__ = "solution_administrations"
	id = Column(Integer, primary_key=True)
	solutions = relationship("Solution", secondary=solution_association)
	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")
	date = Column(DateTime)
	route = Column(String)
	rate = Column(Float)
	rate_unit_id = Column(String, ForeignKey('measurement_units.id'))
	rate_unit = relationship("MeasurementUnit", foreign_keys=[rate_unit_id])
	dose = Column(Float)
	dose_unit_id = Column(String, ForeignKey('measurement_units.id'))
	dose_unit = relationship("MeasurementUnit", foreign_keys=[dose_unit_id])

	def __repr__(self):
		return "<Solution Administration(date='%s', animal_weight='%s%s')>"\
		% (self.date, self.animal_weight, self.animal_weight_unit)

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
	weight = relationship("Weight")
	solution_administration_id = Column(Integer, ForeignKey('solution_administrations.id'))
	solution_administration = relationship("SolutionAdministration", backref=backref("animals"))

	cage_id = Column(Integer, ForeignKey('cages.id'))
	cage = relationship("Cage", back_populates="animals")

	fmri_measurements = relationship("FMRIMeasurement", backref="animal")

	genotypes = relationship("Genotype", secondary=genotype_association, backref="animals")
	treatments = relationship("ChronicTreatment", secondary=treatment_association, backref="animals")

	observations = relationship("Observation")
	uncategorized_treatments = relationship("UncategorizedTreatment")

	def __repr__(self):
		return "<Animal(id='%s', id_eth='%s', cage_eth='%s', id_uzh='%s', cage_uzh='%s', genotype='%s', sex='%s', ear_punches='%s', treatment='%s')>"\
		% (self.id, self.id_eth, self.cage_eth, self.id_uzh, self.cage_uzh, [self.genotype[i].name+" "+self.genotype[i].zygosity for i in range(len(self.genotype))], self.sex, self.ear_punches,[self.treatment[i].solution for i in range(len(self.treatment))])

class Cage(Base):
	__tablename__ = "cages"
	id = Column(Integer, primary_key=True)
	id_uzh = Column(Integer, unique=True)
	location = Column(String)

	handling_habituations = relationship(HandlingHabituation)

	animals = relationship("Animal", back_populates="cage")

class Genotype(Base):
	__tablename__ = "genotypes"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	zygosity = Column(String)

	def __repr__(self):
		return "<Genotype(name='%s', zygosity='%s')>"\
		% (self.name, self.zygosity)

class Weight(Base):
	__tablename__ = "weights"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")
	weight = Column(Float)
	weight_unit_id = Column(String, ForeignKey('measurement_units.id'))
	weight_unit = relationship("MeasurementUnit", foreign_keys=[weight_unit_id])
	animal_id = Column(Integer, ForeignKey("animals.id"))

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

	duration_unit_id = Column(String, ForeignKey('measurement_units.id'))
	duration_unit = relationship("MeasurementUnit", foreign_keys=[duration_unit_id])
	#temperature - usually in degrees Centigrade
	temperature_unit_id = Column(String, ForeignKey('measurement_units.id'))
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
	mass_unit_id = Column(String, ForeignKey('measurement_units.id'))
	mass_unit = relationship("MeasurementUnit", foreign_keys=[mass_unit_id])
	digestion_buffer_id = Column(String, ForeignKey("solutions.id"))
	digestion_buffer = relationship("Solution", foreign_keys=[digestion_buffer_id])
	digestion_buffer_volume = Column(Float)
	digestion_id = Column(Integer, ForeignKey("incubations.id"))
	digestion = relationship("Incubation", foreign_keys=[digestion_id])
	lysis_buffer_id = Column(String, ForeignKey("solutions.id"))
	lysis_buffer = relationship("Solution", foreign_keys=[lysis_buffer_id])
	lysis_buffer_volume = Column(Float)
	lysis_id = Column(Integer, ForeignKey("incubations.id"))
	lysis = relationship("Incubation", foreign_keys=[lysis_id])
	proteinase_id = Column(String, ForeignKey("solutions.id"))
	proteinase = relationship("Solution", foreign_keys=[proteinase_id])
	proteinase_volume = Column(Float)
	inactivation_id = Column(Integer, ForeignKey("incubations.id"))
	inactivation = relationship("Incubation", foreign_keys=[inactivation_id])
	cooling_id = Column(Integer, ForeignKey("incubations.id"))
	cooling = relationship("Incubation", foreign_keys=[cooling_id])
	centrifugation_id = Column(Integer, ForeignKey("incubations.id"))
	centrifugation = relationship("Incubation", foreign_keys=[centrifugation_id])

	volume_unit_id = Column(String, ForeignKey('measurement_units.id'))
	volume_unit = relationship("MeasurementUnit", foreign_keys=[volume_unit_id])
