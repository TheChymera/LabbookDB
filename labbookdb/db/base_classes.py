import datetime
from sqlalchemy import Column, Integer, String, Sequence, Table, ForeignKey, Float, DateTime, Boolean, ForeignKeyConstraint
from sqlalchemy.orm import validates, backref, relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from .utils import *

authors_association = Table('authors_associations', Base.metadata,
	Column('protocols_id', Integer, ForeignKey('protocols.id')),
	Column('operators_id', Integer, ForeignKey('operators.id'))
	)
measurements_irregularities_association = Table('measurements_irregularities_association', Base.metadata,
	Column('measurements_id', Integer, ForeignKey('measurements.id')),
	Column('irregularities_id', Integer, ForeignKey('irregularities.id'))
	)
operations_irregularities_association = Table('operations_irregularities_association', Base.metadata,
	Column('operations_id', Integer, ForeignKey('operations.id')),
	Column('irregularities_id', Integer, ForeignKey('irregularities.id'))
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
	resonator = Column(String)

class StimulationEvent(Base):
	__tablename__ = "stimulation_events"
	id = Column(Integer, primary_key=True)
	#tme values specified in seconds, frequencies in hertz, wavelength in nm
	onset = Column(Float)
	duration = Column(Float)
	frequency = Column(Float)
	pulse_width = Column(Float)
	trial_type = Column(String)
	target = Column(String)
	wavelength = Column(Float)
	strength = Column(Float)
	unit_id = Column(Integer, ForeignKey('measurement_units.id'))
	unit = relationship("MeasurementUnit")

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

class Virus(Base):
	__tablename__ = "viruses"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	addgene_identifier = Column(String)
	capsid = Column(String)
	concentration = Column(Float) # in vg/ml
	plasmid_summary = Column(String)
	credit = Column(String)
	source = Column(String)

	def __str__(self):
		if self.addgene_id:
			return "Virus(code: {code}, Addgene: #{addgene_id})"\
			.format(code=self.code, addgene_id=self.addgene_id)
		else:
			return "Virus(code: {code})"\
			.format(code=self.code)

class OpticFiberImplant(Base):
	__tablename__ = "implants"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	long_code = Column(String) #not necessarily uniqu, as we track different transmittances per model
	angle = Column(Float) # in degrees, relative to an unangled implant axis
	ferrule_diameter = Column(Float) # in mm
	cannula_diameter = Column(Float) # in mm
	length = Column(Float) # in mm
	manufacturer_code = Column(String)
	manufacturer = Column(String)
	numerical_apperture = Column(Float)
	transmittance = Column(Float) # in percent

	def __str__(self):
		return "OpticFiberImplant(code: {code}, long_code: {long_code})"\
		.format(code=self.code, long_code=self.long_code)

class OrthogonalStereotacticTarget(Base):
	__tablename__ = "orthogonal_stereotactic_targets"
	id = Column(Integer, primary_key=True)
	code = Column(String, unique=True)
	reference = Column(String)
	# coordinates in millimetres
	posteroanterior = Column(Float)
	leftright = Column(Float)
	superoinferior = Column(Float)
	# angles in degrees and relative to implant
	pitch = Column(Float)
	yaw = Column(Float)
	roll = Column(Float)
	# depth in millimetres
	depth = Column(Float)
	qualitative_depth_reference = Column(String, default="skull") # set to "dura" if the insertable is lowered to the dura before coordinate setting

	def __str__(self):
		return "OrthogonalStereotacticTarget({reference}: {pa}(PA), {lr}(LR), {si}(SI))"\
		.format(reference=self.reference, pa=self.posteroanterior, lr=self.leftright, si=self.superoinferior)

class Measurement(Base):
	__tablename__ = "measurements"
	id = Column(Integer, primary_key=True)
	date = Column(DateTime)

	animal_id = Column(Integer, ForeignKey('animals.id')) # only set in per-animal measurements
	cage_id = Column(Integer, ForeignKey('cages.id')) # only set in per-cage measurements

	irregularities = relationship("Irregularity", secondary=measurements_irregularities_association)
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
