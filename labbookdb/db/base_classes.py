from sqlalchemy import Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime, Boolean, ForeignKeyConstraint
from sqlalchemy.orm import validates, backref, relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

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
