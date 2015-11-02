from sqlalchemy import create_engine
engine = create_engine('sqlite:///data.db', echo=False)

from common_classes import Animal, Genotype

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker
# Session = sessionmaker(bind=engine)
# session = Session()

def loadSession():
	""""""
	metadata = Base.metadata
	Session = sessionmaker(bind=engine)
	session = Session()
	return session

session = loadSession()
for row in session.query(Animal).order_by(Animal.id):
	print row.__repr__
