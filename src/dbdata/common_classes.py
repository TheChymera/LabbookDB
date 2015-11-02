from sqlalchemy import create_engine
from os import path
db_path = "sqlite:///" + path.expanduser("~/data.db")
engine = create_engine(db_path, echo=False)

from sqlalchemy import Column, Integer, String, Sequence, Table, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import backref, relationship

from sqlalchemy.orm import sessionmaker
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
	administration = Column(String)

	def __repr__(self):
		return "<Treatment(substance='%s', frequency='%s', administration='%s')>"\
		% (self.substance, self.frequency, self.administration)

class Animal(Base):
	__tablename__ = "animals"

	id = Column(Integer, Sequence("substance_id_seq"), primary_key=True)
	id_eth = Column(String)
	cage_eth = Column(String)
	id_uzh = Column(String)
	cage_uzh = Column(String)
	genotype = relationship("Genotype", secondary=genotype_association, backref="animals")
	sex = Column(String)
	ear_punches = Column(String)
	treatment = relationship("Treatment", secondary=treatment_association, backref="animals")

	def __repr__(self):
		return "<Animal(id_eth='%s', cage_eth='%s', id_uzh='%s', cage_uzh='%s', genotype='%s', sex='%s', ear_punches='%s', treatment='%s')>"\
		% (self.id_eth, self.cage_eth, self.id_uzh, self.cage_uzh, [self.genotype[i].name+" "+self.genotype[i].zygosity for i in range(len(self.genotype))], self.sex, self.ear_punches, self.treatment[0].substance)

Base.metadata.create_all(engine)
