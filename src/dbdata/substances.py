from sqlalchemy import create_engine
engine = create_engine('sqlite:///substances.db', echo=False)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy import Column, Integer, String, Sequence, Table, ForeignKey
from sqlalchemy.orm import backref, relationship

association_table = Table('association', Base.metadata,
	Column('substances_id1', Integer, ForeignKey('substances.id')),
	Column('substances_id2', Integer, ForeignKey('substances.id'))
)

class Substance(Base):
	__tablename__ = 'substances'

	id = Column(Integer, Sequence("substance_id_seq"), primary_key=True)
	name = Column(String)
	fullname = Column(String)
	hazards = Column(String)
	contains = relationship("Substance", secondary=association_table, backref="contained")

	def __repr__(self):
		return "<Substance(name='%s', fullname='%s', hazards='%s')>" % (self.name, self.fullname, self.hazards)
Base.metadata.create_all(engine)

edta = Substance(name="EDTA", fullname="Ethylenediaminetetraacetic acid", hazards=None)
sds = Substance(name="SDS", fullname="Sodium Dodecyl Sulfate", hazards="Irritant")
ehqb = Substance(name="EHQb", fullname="Extraction protocol by Hannes, Quick version, buffer", hazards="Irritant")
evssab = Substance(name="EVSsab", fullname="Extraction protocol by Viviane, Slow version, solution a and b", hazards="Irritant")
ehqb.contains = [sds, edta]
ehqb.contains = [sds]
print ehqb.contains[0].name
session.add(edta, sds, ehqb, evssab)

session.commit()

# subs = session.query(Substance).filter_by(name='EDTA').first()
conn = engine.connect()
print conn
