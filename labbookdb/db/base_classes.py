import datetime
from sqlalchemy import Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime, Boolean, ForeignKeyConstraint
from sqlalchemy.orm import validates, backref, relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

def dt_format(dt):
	if not dt:
		return "ONGOING"
	elif dt.time()==datetime.time(0,0,0):
		return dt.date()
	else:
		return dt

authors_association = Table('authors_associations', Base.metadata,
	Column('protocols_id', Integer, ForeignKey('protocols.id')),
	Column('operators_id', Integer, ForeignKey('operators.id'))
	)

class Genotype(Base):
	__tablename__ = "genotypes"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	construct = Column(String)
	zygosity = Column(String)

	def __repr__(self):
		return "<Genotype(code='%s', construct='%s' zygosity='%s')>"\
		% (self.code, self.construct, self.zygosity)

class Irregularity(Base):
	__tablename__ = "irregularities"
	id = Column(Integer, primary_key=True)
	description = Column(String, unique=True)

class MeasurementUnit(Base):
	__tablename__ = "measurement_units"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	long_name = Column(String)
	siunitx = Column(String)

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


#fMRI classes:

class FMRIScannerSetup(Base):
	__tablename__ = "fmri_scanner_setups"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	coil = Column(String)
	scanner = Column(String)
	support = Column(String)

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

#meta classes:

class Biopsy(Base):
	__tablename__ = "biopsies"
	id = Column(Integer, primary_key=True)
	start_date = Column(DateTime)
	animal_id = Column(Integer, ForeignKey('animals.id'))
	extraction_protocol_id = Column(Integer, ForeignKey('protocols.id'))
	extraction_protocol = relationship("Protocol", foreign_keys=[extraction_protocol_id])
	sample_location = Column(String) #id of the physical sample
	fluorescent_microscopy = relationship("FluorescentMicroscopyMeasurement", backref="biopsy")
	type = Column(String(50))
	__mapper_args__ = {
		'polymorphic_identity': 'biopsy',
		'polymorphic_on': type
		}

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

	def __str__(self):
		return "Protocol(code: {code})"\
		.format(code=self.code)

class Measurement(Base):
	__tablename__ = "measurements"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)

	animal_id = Column(Integer, ForeignKey('animals.id')) # only set in per-animal measurements
	cage_id = Column(Integer, ForeignKey('cages.id')) # only set in per-cage measurements

	operator_id = Column(Integer, ForeignKey('operators.id'))
	operator = relationship("Operator")

	type = Column(String(50))
	__mapper_args__ = {
		'polymorphic_identity': 'measurement',
		'polymorphic_on': type
		}

	def __str__(self):
		return "{type}(date: {date})"\
		.format(date=dt_format(self.date), type=self.type)
