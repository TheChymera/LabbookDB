from sqlalchemy import create_engine
engine = create_engine('sqlite:///data.db', echo=False)

from sqlalchemy import Column, Integer, String, Sequence, Table, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import backref, relationship

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

association_table = Table('association', Base.metadata,
	Column('genotypes_id', Integer, ForeignKey('genotypes.id')),
	Column('animals_id', Integer, ForeignKey('animals.id'))
)

class Genotype(Base):
	__tablename__ = "genotypes"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	zygosity = Column(String)

class Animal(Base):
	__tablename__ = "animals"

	id = Column(Integer, Sequence("substance_id_seq"), primary_key=True)
	id_eth = Column(String)
	cage_eth = Column(String)
	id_uzh = Column(String)
	cage_uzh = Column(String)
	genotype = relationship("Genotype", secondary=association_table, backref="animals")
	sex = Column(String)
	ear_punches = Column(String)

	def __repr__(self):
		return "<Substance(id_eth='%s', cage_eth='%s', id_uzh='%s', cage_uzh='%s', genotype='%s', sex='%s', ear_punches='%s')>"\
		 % (self.id_eth, self.cage_eth, self.id_uzh, self.cage_uzh, [self.genotype[i].name+" "+self.genotype[i].zygosity for i in range(len(self.genotype))], self.sex, self.ear_punches)

Base.metadata.create_all(engine)
