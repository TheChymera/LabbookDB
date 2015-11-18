from sqlalchemy import create_engine, Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime
from sqlalchemy.orm import backref, relationship, sessionmaker
from os import path
db_path = "sqlite:///" + path.expanduser("~/data.db")
engine = create_engine(db_path, echo=False)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

genotype_association = Table('gt_association', Base.metadata,
	Column('genotypes_id', Integer, ForeignKey('genotypes.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)
treatment_association = Table('tr_association', Base.metadata,
	Column('treatments_id', Integer, ForeignKey('treatments.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)
administration_association = Table('ad_association', Base.metadata,
	Column('administrations_id', Integer, ForeignKey('substance_administration.id')),
	Column('treatments_id', Integer, ForeignKey('treatments.id'))
)

class InhalationAnesthesia(Base):
	__tablename__ = "inhalation_anesthesia"
	id = Column(Integer, primary_key=True)
	anesthetic = Column(String)
	concentration = Column(Float)
	concentration_unit = Column(String)
	duration = Column(String)

	def __repr__(self):
		return "<Inhalation Anesthesia Step(anesthetic='%s', concentration='%s', duration='%s')>"\
		% (self.anesthetic, self.concentration, self.duration)

class ScannerSetup(Base):
	__tablename__ = "scanner_setup"
	id = Column(Integer, primary_key=True)
	coil = Column(String)
	respiraion = Column(Float)
	support = Column(Float)
	primary_rate = Column(Float)
	secondary_rate = Column(Float)

class SubstanceAdministration(Base):
	__tablename__ = "substance_administration"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	animal_weight = Column(Float)
	animal_weight_unit = Column(String)

class TwoStepInjectionAnesthesia(Base):
	__tablename__ = "twostep_injection_anesthesia"
	id = Column(Integer, primary_key=True)
	anesthetic = Column(String)
	concentration = Column(Float)
	concentration_unit = Column(String)
	primary_dose = Column(Float)
	primary_rate = Column(Float)
	secondary_rate = Column(Float)

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
	substance_administrations = relationship("SubstanceAdministration", secondary=administration_association, backref="treatments")

	def __repr__(self):
		return "<Treatment(substance='%s', frequency='%s', route='%s')>"\
		% (self.substance, self.frequency, self.route)

class Animal(Base):
	__tablename__ = "animals"
	id = Column(Integer, Sequence("substance_id_seq"), primary_key=True)
	id_eth = Column(String)
	cage_eth = Column(String)
	id_uzh = Column(String)
	cage_uzh = Column(String)
	sex = Column(String)
	ear_punches = Column(String)

	genotype = relationship("Genotype", secondary=genotype_association, backref="animals")
	treatment = relationship("Treatment", secondary=treatment_association, backref="animals")

	def __repr__(self):
		return "<Animal(id_eth='%s', cage_eth='%s', id_uzh='%s', cage_uzh='%s', genotype='%s', sex='%s', ear_punches='%s', treatment='%s')>"\
		% (self.id_eth, self.cage_eth, self.id_uzh, self.cage_uzh, [self.genotype[i].name+" "+self.genotype[i].zygosity for i in range(len(self.genotype))], self.sex, self.ear_punches, [self.treatment[i].substance for i in range(len(self.treatment))])

Base.metadata.create_all(engine)
