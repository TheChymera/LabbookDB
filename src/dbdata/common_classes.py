from sqlalchemy import create_engine, Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime
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
	scanners_setup = relationship("ScannerSetup", backref="used_for_protocols")
	induction_anesthesia = relationship("InhalationAnesthesia", backref="used_in")
	maintenance_anesthesia = relationship("InhalationAnesthesia", backref="used_in")


class InhalationAnesthesia(Base):
	__tablename__ = "inhalation_anesthesias"
	id = Column(Integer, primary_key=True)
	anesthetic = Column(String)
	concentration = Column(Float)
	concentration_unit = Column(String)
	duration = Column(Float)
	duration_unit = Column(String)

	def __repr__(self):
		return "<Inhalation Anesthesia Step(anesthetic='%s', concentration='%s', duration='%s')>"\
		% (self.anesthetic, self.concentration, self.duration)

class ScannerSetup(Base):
	__tablename__ = "scanner_setups"
	id = Column(Integer, primary_key=True)
	coil = Column(String)
	respiraion = Column(String)
	support = Column(String)

class SubstanceAdministration(Base):
	__tablename__ = "substance_administrations"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	animal_weight = Column(Float)
	animal_weight_unit = Column(String)
	treatment_id = Column(Integer, ForeignKey('treatments.id'))

	def __repr__(self):
		return "<Substance Administration(date='%s', animal_weight='%s%s')>"\
		% (self.date, self.animal_weight, self.animal_weight_unit)

class TwoStepInjectionAnesthesia(Base):
	__tablename__ = "twostep_injection_anesthesias"
	id = Column(Integer, primary_key=True)
	anesthetic = Column(String)
	solution_concentration = Column(Float)
	solution_concentration_unit = Column(String)
	primary_dose = Column(Float)
	primary_rate = Column(Float)
	primary_rate_unit = Column(String)
	secondary_rate = Column(Float)
	secondary_rate_unit = Column(String)

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
