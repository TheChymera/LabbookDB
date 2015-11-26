from sqlalchemy import create_engine, Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime, ForeignKeyConstraint
from sqlalchemy.orm import backref, relationship, sessionmaker
from os import path

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

genotype_association = Table('gt_association', Base.metadata,
	Column('genotypes_id', Integer, ForeignKey('genotypes.id')),
	Column('animals_id', Integer, ForeignKey('animals.id_eth'))
)
treatment_association = Table('tr_association', Base.metadata,
	Column('treatments_id', Integer, ForeignKey('treatments.code')),
	Column('animals_id', Integer, ForeignKey('animals.id_eth'))
)
substance_association = Table('st_association', Base.metadata,
	Column('substance_administrations_id', Integer, ForeignKey('substance_administrations.id')),
	Column('solutions_id', Integer, ForeignKey('solutions.code'))
)
operator_association = Table('op_association', Base.metadata,
	Column('operator_id', Integer, ForeignKey('operators.initials')),
	Column('fmri_measurement_sessions_id', Integer, ForeignKey('fmri_measurement_sessions.id'))
)
ingredients_association = Table('ig_association', Base.metadata,
	Column('solutions_id', Integer, ForeignKey('solutions.code')),
	Column('ingredients_id', Integer, ForeignKey('ingredients.id'))
)

class FMRIMeasurementSession(Base):
	__tablename__ = "fmri_measurement_sessions"
	id = Column(Integer, primary_key=True)
	operator = relationship("Operator", secondary=operator_association, backref="performed_fmri_mesurements")
	date = Column(DateTime)
	animal_id = Column(Integer, ForeignKey('animals.id_eth'))
	animal = relationship("Animal", backref="measurements")
	protocol_id = Column(Integer, ForeignKey('fmri_measurement_protocols.id'))
	protocol = relationship("FMRIMeasurementProtocol", backref="used_in_sessions")
	animal_weight = Column(Float)
	animal_weight_unit_id = Column(String, ForeignKey('measurement_units.code'))
	animal_weight_unit = relationship("MeasurementUnit", foreign_keys=[animal_weight_unit_id])

class FMRIMeasurementProtocol(Base):
	__tablename__ = "fmri_measurement_protocols"
	id = Column(Integer, primary_key=True)
	scanner_setup_id = Column(Integer, ForeignKey('scanner_setups.id'))
	scanner_setup = relationship("ScannerSetup", backref="used_for_protocols")
	induction_anesthesia_gas_id = Column(Integer, ForeignKey('substance_administrations.id'))
	induction_anesthesia_gas = relationship("SubstanceAdministration", foreign_keys=[induction_anesthesia_gas_id])
	induction_anesthesia_injection_id = Column(Integer, ForeignKey('substance_administrations.id'))
	induction_anesthesia_injection = relationship("SubstanceAdministration", foreign_keys=[induction_anesthesia_injection_id])
	maintenance_anesthesia_gas_id = Column(Integer, ForeignKey('substance_administrations.id'))
	maintenance_anesthesia_gas = relationship("SubstanceAdministration", foreign_keys=[maintenance_anesthesia_gas_id])
	maintenance_anesthesia_injection_id = Column(Integer, ForeignKey('substance_administrations.id'))
	maintenance_anesthesia_injection = relationship("SubstanceAdministration", foreign_keys=[maintenance_anesthesia_injection_id])

class MeasurementUnit(Base):
	__tablename__ = "measurement_units"
	code = Column(String, primary_key=True)
	long_name = Column(String)
	siunitx = Column(String)

class LaserStimulationProtocol(Base):
	__tablename__ = "laser_stimulation_protocols"
	id = Column(Integer, primary_key=True)
	stimulus_repetitions = Column(Integer)
	stimulus_duration = Column(Float)
	inter_stimulus_duration = Column(Float)
	stimulation_onset = Column(Float)
	stimulus_frequency = Column(Float)
	pulse_width = Column(Float)
	duration_unit_id = Column(String, ForeignKey('measurement_units.code'))
	duration_unit = relationship("MeasurementUnit", foreign_keys=[duration_unit_id])
	frequency_unit_id = Column(String, ForeignKey('measurement_units.code'))
	frequency_unit = relationship("MeasurementUnit", foreign_keys=[frequency_unit_id])

class ScannerSetup(Base):
	__tablename__ = "scanner_setups"
	id = Column(Integer, primary_key=True)
	coil = Column(String)
	respiration = Column(String)
	support = Column(String)

class TreatmentAdministration(Base):
	__tablename__ = "treatment_administrations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	operator_id = Column(Integer, ForeignKey('operators.initials'))
	operator = relationship("Operator", backref="administederd_substances")
	animal_id = Column(Integer, ForeignKey('animals.id_eth'))
	animal = relationship("Animal", backref="administrations")
	animal_weight = Column(Float)
	animal_weight_unit_id = Column(String, ForeignKey('measurement_units.code'))
	animal_weight_unit = relationship("MeasurementUnit", foreign_keys=[animal_weight_unit_id])
	substance_administration_id = Column(Integer, ForeignKey('substance_administrations.id'))
	substance_administration = relationship("SubstanceAdministration")

	treatment_id = Column(Integer, ForeignKey("treatments.code"))

class SubstanceAdministration(Base):
	__tablename__ = "substance_administrations"
	id = Column(Integer, primary_key=True)
	substance = relationship("Solution", secondary=substance_association, backref="administered")
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

class Genotype(Base):
	__tablename__ = "genotypes"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	zygosity = Column(String)

	def __repr__(self):
		return "<Genotype(name='%s', zygosity='%s')>"\
		% (self.name, self.zygosity)

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

class Treatment(Base):
	__tablename__ = "treatments"
	code = Column(String, primary_key=True)
	name = Column(String)
	frequency = Column(String)
	route = Column(String)
	administrations = relationship("TreatmentAdministration", backref="treatment")

	def __repr__(self):
		return "<Treatment(substance='%s', frequency='%s', route='%s', administrations='%s')>"\
		% (self.substance, self.frequency, self.route, self.substance_administrations)

class Operator(Base):
	__tablename__ = "operators"
	initials = Column(String, primary_key=True)
	full_name = Column(String)
	affiliation = Column(String)

class Biopsy(Base):
	__tablename__ = "biopsies"
	code = Column(String, primary_key=True)
	extracted = Column(DateTime)
	animal_id = Column(Integer, ForeignKey('animals.id_eth'))
	animal = relationship("Animal")
	tissue = Column(String)

class Animal(Base):
	__tablename__ = "animals"
	id_eth = Column(Integer, primary_key=True)
	cage_eth = Column(Integer)
	id_uzh = Column(String)
	cage_uzh = Column(String)
	sex = Column(String)
	ear_punches = Column(String)

	genotype = relationship("Genotype", secondary=genotype_association, backref="animals")
	treatment = relationship("Treatment", secondary=treatment_association, backref="animals")

	def __repr__(self):
		return "<Animal(id_eth='%s', cage_eth='%s', id_uzh='%s', cage_uzh='%s', genotype='%s', sex='%s', ear_punches='%s', treatment='%s')>"\
		% (self.id_eth, self.cage_eth, self.id_uzh, self.cage_uzh, [self.genotype[i].name+" "+self.genotype[i].zygosity for i in range(len(self.genotype))], self.sex, self.ear_punches, [self.treatment[i].substance for i in range(len(self.treatment))])
