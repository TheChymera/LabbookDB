from sqlalchemy import create_engine, Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime, ForeignKeyConstraint
from sqlalchemy.orm import backref, relationship, sessionmaker
from os import path

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

genotype_association = Table('gt_association', Base.metadata,
	Column('genotypes_id', Integer, ForeignKey('genotypes.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)
treatment_association = Table('tr_association', Base.metadata,
	Column('chronic_treatments_id', Integer, ForeignKey('chronic_treatments.code')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)
substance_association = Table('st_association', Base.metadata,
	Column('substance_administrations_id', Integer, ForeignKey('substance_administrations.id')),
	Column('solutions_id', Integer, ForeignKey('solutions.code'))
)
operator_association = Table('op_association', Base.metadata,
	Column('operator_id', Integer, ForeignKey('operators.initials')),
	Column('fmri_measurements_id', Integer, ForeignKey('fmri_measurements.id'))
)
ingredients_association = Table('ig_association', Base.metadata,
	Column('solutions_id', Integer, ForeignKey('solutions.code')),
	Column('ingredients_id', Integer, ForeignKey('ingredients.id'))
)
laser_association = Table('ls_association', Base.metadata,
	Column('laser_stimulation_protocols_id', Integer, ForeignKey('laser_stimulation_protocols.code')),
	Column('fmri_measurements_id', Integer, ForeignKey('fmri_measurements.id'))
)

#general classes:

class Operator(Base):
	__tablename__ = "operators"
	initials = Column(String, primary_key=True)
	full_name = Column(String)
	affiliation = Column(String)

class MeasurementUnit(Base):
	__tablename__ = "measurement_units"
	code = Column(String, primary_key=True)
	long_name = Column(String)
	siunitx = Column(String)

class Ingredient(Base):
	__tablename__ = "ingredients"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	concentration = Column(Float, default=100)
	concentration_unit_id = Column(String, ForeignKey('measurement_units.code'))
	concentration_unit = relationship("MeasurementUnit")
	supplier = Column(String)
	supplier_id = Column(String)
	contained = Column(Integer, ForeignKey("ingredients.id"))
	contains = relationship("Ingredient")

class Solution(Base):
	__tablename__ = "solutions"
	code = Column(String, primary_key=True)
	name = Column(String)
	supplier = Column(String)
	supplier_id = Column(String)
	contains = relationship("Ingredient", secondary=ingredients_association, backref="ingredient_of")

	def __repr__(self):
		return "<Solution(name='%s' (long_name='%s'), concentration=%s%s contains: %s)>"\
		% (self.name, self.long_name, self.concentration, self.concentration_unit, self.contains)

#fMRI classes:

class FMRIScannerSetup(Base):
	__tablename__ = "scanner_setups"
	code = Column(String, primary_key=True)
	coil = Column(String)
	support = Column(String)

class FMRIMeasurement(Base):
	__tablename__ = "fmri_measurements"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	operator_id = Column(Integer, ForeignKey('operators.initials'))
	operator = relationship("Operator", backref="fmri_measurements")
	preparation_id = Column(Integer, ForeignKey('fmri_animal_preparation_protocols.code'))
	preparation = relationship("FMRIAnimalPreparationProtocol", backref="used_in_sessions")
	laser_stimulation_list = relationship("LaserStimulationProtocol", secondary=laser_association, backref="used_in")
	scanner_setup_id = Column(Integer, ForeignKey('scanner_setups.code'))
	scanner_setup = relationship("FMRIScannerSetup", backref="used_for_protocols")
	animal_id = Column(Integer, ForeignKey('animals.id'))

class FMRIAnimalPreparationProtocol(Base):
	__tablename__ = "fmri_animal_preparation_protocols"
	code = Column(String, primary_key=True)
	induction_anesthesia_gas_id = Column(Integer, ForeignKey('substance_administrations.id'))
	induction_anesthesia_gas = relationship("SubstanceAdministration", foreign_keys=[induction_anesthesia_gas_id])
	induction_anesthesia_injection_id = Column(Integer, ForeignKey('substance_administrations.id'))
	induction_anesthesia_injection = relationship("SubstanceAdministration", foreign_keys=[induction_anesthesia_injection_id])
	maintenance_anesthesia_gas_id = Column(Integer, ForeignKey('substance_administrations.id'))
	maintenance_anesthesia_gas = relationship("SubstanceAdministration", foreign_keys=[maintenance_anesthesia_gas_id])
	maintenance_anesthesia_injection_id = Column(Integer, ForeignKey('substance_administrations.id'))
	maintenance_anesthesia_injection = relationship("SubstanceAdministration", foreign_keys=[maintenance_anesthesia_injection_id])
	respiration = Column(String)

class LaserStimulationProtocol(Base):
	__tablename__ = "laser_stimulation_protocols"
	code = Column(String, primary_key=True)
	#tme values specified in seconds, frequencies in hertz
	stimulus_repetitions = Column(Integer)
	stimulus_duration = Column(Float)
	inter_stimulus_duration = Column(Float)
	stimulation_onset = Column(Float)
	stimulus_frequency = Column(Float)
	pulse_width = Column(Float)

#treatment classes:

class ChronicTreatmentAdministration(Base):
	__tablename__ = "chronic_treatment_administrations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	deviating_substance_amount = Column(Integer)
	operator_id = Column(Integer, ForeignKey('operators.initials'))
	operator = relationship("Operator", backref="administederd_treatments")
	treatment_id = Column(Integer, ForeignKey("chronic_treatments.code"))

class ChronicTreatment(Base):
	__tablename__ = "chronic_treatments"
	code = Column(String, primary_key=True)
	name = Column(String)
	frequency = Column(String)
	route = Column(String)
	rate = Column(Float)
	rate_unit_id = Column(String, ForeignKey('measurement_units.code'))
	rate_unit = relationship("MeasurementUnit", foreign_keys=[rate_unit_id])
	dose = Column(Float)
	dose_unit_id = Column(String, ForeignKey('measurement_units.code'))
	dose_unit = relationship("MeasurementUnit", foreign_keys=[dose_unit_id])
	administrations = relationship("ChronicTreatmentAdministration")

class SubstanceAdministration(Base):
	__tablename__ = "substance_administrations"
	id = Column(Integer, primary_key=True)
	substance = relationship("Solution", secondary=substance_association, backref="administered")
	operator_id = Column(Integer, ForeignKey('operators.initials'))
	operator = relationship("Operator", backref="administederd_substances")
	date = Column(DateTime)
	route = Column(String)
	rate = Column(Float)
	rate_unit_id = Column(String, ForeignKey('measurement_units.code'))
	rate_unit = relationship("MeasurementUnit", foreign_keys=[rate_unit_id])
	dose = Column(Float)
	dose_unit_id = Column(String, ForeignKey('measurement_units.code'))
	dose_unit = relationship("MeasurementUnit", foreign_keys=[dose_unit_id])

	def __repr__(self):
		return "<Substance Administration(date='%s', animal_weight='%s%s')>"\
		% (self.date, self.animal_weight, self.animal_weight_unit)

#animal classes:

class Animal(Base):
	__tablename__ = "animals"
	id = Column(Integer, primary_key=True)
	id_eth = Column(Integer)
	cage_eth = Column(Integer)
	id_uzh = Column(String)
	cage_uzh = Column(String)
	sex = Column(String)
	ear_punches = Column(String)

	death_date = Column(DateTime)
	death_reason = Column(String)
	weight = relationship("Weight")
	substance_administration_id = Column(Integer, ForeignKey('substance_administrations.id'))
	substance_administration = relationship("SubstanceAdministration", backref=backref("animals"))

	fmri_measurements = relationship("FMRIMeasurement", backref="animal")

	genotype = relationship("Genotype", secondary=genotype_association, backref="animals")
	treatment = relationship("ChronicTreatment", secondary=treatment_association, backref="animals")

	def __repr__(self):
		return "<Animal(id='%s', id_eth='%s', cage_eth='%s', id_uzh='%s', cage_uzh='%s', genotype='%s', sex='%s', ear_punches='%s', treatment='%s')>"\
		% (self.id, self.id_eth, self.cage_eth, self.id_uzh, self.cage_uzh, [self.genotype[i].name+" "+self.genotype[i].zygosity for i in range(len(self.genotype))], self.sex, self.ear_punches, [self.treatment[i].substance for i in range(len(self.treatment))])

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
	operator_id = Column(Integer, ForeignKey('operators.initials'))
	operator = relationship("Operator", backref="weighing_sessions")
	weight = Column(Float)
	weight_unit_id = Column(String, ForeignKey('measurement_units.code'))
	weight_unit = relationship("MeasurementUnit", foreign_keys=[weight_unit_id])
	animal_id = Column(Integer, ForeignKey("animals.id"))

class BioticSample(Base):
	__tablename__ = "biotic_samples"
	code = Column(String, primary_key=True)
	extracted = Column(DateTime)
	discriminator = Column('type', String(50))
	__mapper_args__ = {'polymorphic_on': discriminator}

class AnimalBiopsy(BioticSample):
	__tablename__ = "animal_biopsies"
	__mapper_args__ = {'polymorphic_identity': 'animal_biopsy'}
	code = Column(String, ForeignKey('biotic_samples.code'), primary_key=True)
	animal_id = Column(Integer, ForeignKey('animals.id'))
	animal = relationship("Animal")
	tissue = Column(String)

# DNA classes:
class Incubation(Base):
	__tablename__ = "incubations"
	id = Column(Integer, primary_key=True)
	speed = Column(Float)
	duration = Column(Float)
	temperature = Column(Float)
	movement = Column(String) # "centrifuge" or "shake"

	#speed - usually in RPM - will refer to either centrifugation or shaking (See above)
	speed_unit_id = Column(String, ForeignKey('measurement_units.code'))
	speed_unit = relationship("MeasurementUnit", foreign_keys=[speed_unit_id])
	duration_unit_id = Column(String, ForeignKey('measurement_units.code'))
	duration_unit = relationship("MeasurementUnit", foreign_keys=[duration_unit_id])
	temperature_unit_id = Column(String, ForeignKey('measurement_units.code'))
	temperature_unit = relationship("MeasurementUnit", foreign_keys=[temperature_unit_id])

class DNAExtraction(Base):
	__tablename__ = "dna_extractions"
	code = Column(String, primary_key=True)
	protocol_id = Column(Integer, ForeignKey('dna_extraction_protocols.code'))
	protocol = relationship('DNAExtractionProtocol', backref='used_for_extractions')
	source_id = Column(Integer, ForeignKey('biotic_samples.code'))
	source = relationship('BioticSample', backref='dna_extractions')

class DNAExtractionProtocol(Base):
	__tablename__ = 'dna_extraction_protocols'
	code = Column(String, primary_key=True)
	name = Column(String)
	sample_mass = Column(Float)
	mass_unit_id = Column(String, ForeignKey('measurement_units.code'))
	mass_unit = relationship("MeasurementUnit", foreign_keys=[mass_unit_id])
	pre_lysis_buffer_id = Column(String, ForeignKey("solutions.code"))
	pre_lysis_buffer = relationship("Solution", foreign_keys=[pre_lysis_buffer_id])
	pre_lysis_buffer_volume = Column(Float)
	pre_lysis_id = Column(Integer, ForeignKey("incubations.id"))
	pre_lysis = relationship("Incubation", foreign_keys=[pre_lysis_id])
	lysis_buffer_id = Column(String, ForeignKey("solutions.code"))
	lysis_buffer = relationship("Solution", foreign_keys=[lysis_buffer_id])
	lysis_buffer_volume = Column(Float)
	proteinase_id = Column(String, ForeignKey("solutions.code"))
	proteinase = relationship("Solution", foreign_keys=[proteinase_id])
	proteinase_volume = Column(Float)
	inactivation_id = Column(Integer, ForeignKey("incubations.id"))
	inactivation = relationship("Incubation", foreign_keys=[pre_lysis_id])
	volume_unit_id = Column(String, ForeignKey('measurement_units.code'))
	volume_unit = relationship("MeasurementUnit", foreign_keys=[volume_unit_id])
	time_unit_id = Column(String, ForeignKey('measurement_units.code'))
	time_unit = relationship("MeasurementUnit", foreign_keys=[time_unit_id])

	discriminator = Column('type', String(50))
	__mapper_args__ = {'polymorphic_on': discriminator}

class QuickDNAExtractionProtocol(DNAExtractionProtocol):
	__tablename__ = 'quick_dna_extraction_protocols'
	__mapper_args__ = {'polymorphic_identity': 'quick'}
	id = Column(String, ForeignKey('dna_extraction_protocols.code'), primary_key=True)
	lysis_preheat_id = Column(Integer, ForeignKey("incubations.id"))
	lysis_preheat = relationship("Incubation", foreign_keys=[lysis_preheat_id])
	cooling_id = Column(Integer, ForeignKey("incubations.id"))
	cooling = relationship("Incubation", foreign_keys=[cooling_id])
	centrifugation_id = Column(Integer, ForeignKey("incubations.id"))
	centrifugation = relationship("Incubation", foreign_keys=[centrifugation_id])
