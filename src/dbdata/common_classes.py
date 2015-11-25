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
	Column('treatments_id', Integer, ForeignKey('treatments.id')),
	Column('animals_id', Integer, ForeignKey('animals.id_eth'))
)

class FMRIMeasurementSession(Base):
	__tablename__ = "fmri_measurement_sessions"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	protocol_id = Column(Integer, ForeignKey('fmri_measurement_protocols.id'))
	protocol = relationship("FMRIMeasurementProtocol", backref="used_in_sessions")

class FMRIMeasurementProtocol(Base):
	__tablename__ = "fmri_measurement_protocols"
	id = Column(Integer, primary_key=True)
	scanner_setup_id = Column(Integer, ForeignKey('scanner_setups.id'))
	scanner_setup = relationship("ScannerSetup", backref="used_for_protocols")
	induction_anesthesia_id = Column(Integer, ForeignKey('substance_administrations.id'))
	induction_anesthesia = relationship("SubstanceAdministration", backref="used_in_protocol")
	maintenance_anesthesia_id = Column(Integer, ForeignKey('twostep_injection_anesthesias.id'))
	maintenance_anesthesia = relationship("TwoStepInjectionAnesthesia", backref="used_in_protocol")


class LaserStimulationProtocol(Base):
	__tablename__ = "laser_stimulation_protocols"
	id = Column(Integer, primary_key=True)
	stimulus_repetitions = Column(Integer)
	stimulus_duration = Column(Float)
	inter_stimulus_duration = Column(Float)
	stimulation_onset = Column(Float)
	stimulus_frequency = Column(Float)
	pulse_width = Column(Float)
	duration_unit = Column(String)
	frequency_unit = Column(String)

class InhalationAnesthesia(Base):
	__tablename__ = "inhalation_anesthesias"
	id = Column(Integer, primary_key=True)
	anesthetic_id = Column(Integer, ForeignKey('solutions.id'))
	anesthetic = relationship("Solution")
	concentration = Column(Float)
	concentration_unit = Column(String, default="%")
	duration = Column(Float)
	duration_unit = Column(String)

	def __repr__(self):
		return "<Inhalation Anesthesia Step(anesthetic='%s', concentration='%s', duration='%s')>"\
		% (self.anesthetic, self.concentration, self.duration)

class ScannerSetup(Base):
	__tablename__ = "scanner_setups"
	id = Column(Integer, primary_key=True)
	coil = Column(String)
	respiration = Column(String)
	support = Column(String)

class SubstanceAdministration(Base):
	__tablename__ = "substance_administrations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	substance_id = Column(Integer, ForeignKey('solutions.id'))
	substance = relationship("Solution", backref="used_in_inhalation")
	route = Column(String)
	animal_weight = Column(Float)
	animal_weight_unit = Column(String)
	treatment_id = Column(Integer, ForeignKey('treatments.id'))

	def __repr__(self):
		return "<Substance Administration(date='%s', animal_weight='%s%s')>"\
		% (self.date, self.animal_weight, self.animal_weight_unit)

class TwoStepInjectionAnesthesia(Base):
	__tablename__ = "twostep_injection_anesthesias"
	id = Column(Integer, primary_key=True)
	anesthetic_id = Column(Integer, ForeignKey('solutions.id'))
	anesthetic = relationship("Solution", backref="used_in_injection")
	primary_dose = Column(Float)
	primary_dose_unit = Column(String, default="ml/g_animal")
	primary_rate = Column(Float, default=20)
	primary_rate_unit = Column(String, default="mul/s")
	secondary_rate = Column(Float)
	secondary_rate_unit = Column(String, default="ml/g_animal/h")

	# def __repr__(self):
	# 	return "<Inhalation Anesthesia Step(anesthetic='%s', concentration='%s', duration='%s')>"\
	# 	% (self.anesthetic, self.concentration, self.duration)

class Genotype(Base):
	__tablename__ = "genotypes"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	zygosity = Column(String)

	def __repr__(self):
		return "<Genotype(name='%s', zygosity='%s')>"\
		% (self.name, self.zygosity)

class Solution(Base):
	__tablename__ = "solutions"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	long_name = Column(String)
	concentration = Column(Float, default=100)
	concentration_unit = Column(String, default="%")
	supplier = Column(String)
	supplier_id = Column(String)
	contained = Column(Integer, ForeignKey("solutions.id"))
	contains = relationship("Solution")

	def __repr__(self):
		return "<Solution(name='%s' (long_name='%s'), concentration=%s%s contains: %s)>"\
		% (self.name, self.long_name, self.concentration, self.concentration_unit, self.contains)

class Treatment(Base):
	__tablename__ = "treatments"
	id = Column(Integer, primary_key=True)
	substance = Column(String)
	frequency = Column(String)
	route = Column(String)
	substance_administrations = relationship("SubstanceAdministration", backref="treatment")

	def __repr__(self):
		return "<Treatment(substance='%s', frequency='%s', route='%s', administrations='%s')>"\
		% (self.substance, self.frequency, self.route, self.substance_administrations)

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
