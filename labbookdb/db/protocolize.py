import subprocess
import tempfile
import shutil
from string import Template
from sqlalchemy import create_engine, literal, inspection
from sqlalchemy.orm import aliased, relation, scoped_session, sessionmaker, eagerload, subqueryload, joinedload, lazyload, Load
from .common_classes import *
from .utils import get_script_dir
import pandas as pd
import os

tables = {"animals": Animal, "dna_extraction_protocols": DNAExtractionProtocol, "substances": Solution, "incubations": Incubation, "measurement_units": MeasurementUnit}

db_path = "sqlite:///" + os.path.expanduser("~/meta.db")
engine = create_engine(db_path, echo=False)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker

def loadSession():
	""""""
	Session = sessionmaker(bind=engine)
	session = Session()
	return session

session = loadSession()

def compose_tex(table, code):

	#!!! for a system-wide install the location should likely be redefined!
	templates_path = os.path.join(get_script_dir(),"text_templates")

	cols = []
	joins = []
	insp = inspection.inspect(tables[table])
	for name, col in insp.columns.items():
		cols.append(col.label(name))
	for name, rel in insp.relationships.items():
		alias = aliased(rel.mapper.class_, name=name)
		joins.append((alias, rel.class_attribute))
		for col_name, col in inspection.inspect(rel.mapper).columns.items():
			#the id column causes double entries, as it is mapped once on the parent table (related_table_id) and once on the child table (table_id)
			if col.key != "id":
				aliased_col = getattr(alias, col.key)
				cols.append(aliased_col.label("{}_{}".format(name, col_name)))

		sub_insp = inspection.inspect(rel.mapper.class_)
		for sub_name, sub_rel in sub_insp.relationships.items():
			if "contains" not in sub_name:
				sub_alias = aliased(sub_rel.mapper.class_, name=name+"_"+sub_name)
				joins.append((sub_alias, sub_rel.class_attribute))
				for sub_col_name, sub_col in inspection.inspect(sub_rel.mapper).columns.items():
					#the id column causes double entries, as it is mapped once on the parent table (related_table_id) and once on the child table (table_id)
					if sub_col.key != "id":
						sub_aliased_col = getattr(sub_alias, sub_col.key)
						cols.append(sub_aliased_col.label("{}_{}_{}".format(name, sub_name, sub_col_name)))

	sql_query = session.query(*cols).select_from(tables[table])
	for join in joins:
		sql_query = sql_query.outerjoin(*join)
	sql_query = sql_query.filter(tables[table].code == code)

	mystring = sql_query.statement
	mydf = pd.read_sql_query(mystring,engine)

	template_keys = [i for i in mydf.columns.tolist()]
	template_values = mydf.ix[0].tolist()
	for ix, template_value in enumerate(template_values):
		try:
			if template_value.is_integer():
				template_values[ix] = int(template_value)
		except AttributeError:
			pass

	templating_dictionary = dict(zip(template_keys, template_values))

	with open(os.path.join(templates_path,'standard_header.tex'), 'r') as myfile:
		standard_header=myfile.read()
	with open(os.path.join(templates_path,'standard_footer.tex'), 'r') as myfile:
		standard_footer=myfile.read()
	with open(os.path.join(templates_path,table+'.tex'), 'r') as myfile:
		template_file=myfile.read()
		tex_template=Template(template_file)
		tex_template = tex_template.substitute(templating_dictionary)

	tex_document = standard_header
	tex_document += tex_template
	tex_document += standard_footer

	session.close()
	engine.dispose()

	return tex_document

def print_document(tex, pdfname="protocol"):
	current = os.getcwd()
	temp = tempfile.mkdtemp()
	os.chdir(temp)

	f = open('protocol.tex','w')
	f.write(tex)
	f.close()

	proc=subprocess.Popen(['pdflatex','protocol.tex'])
	subprocess.Popen(['pdflatex',tex])
	proc.communicate()

	os.rename('protocol.pdf',pdfname)
	shutil.copy(pdfname,current)
	shutil.rmtree(temp)

if __name__ == '__main__':
	code = "EPDqEP"
	table = "dna_extraction_protocols"
	tex=compose_tex(table,code)
	print_document(tex, table[:-1]+"_"+code+".pdf")
