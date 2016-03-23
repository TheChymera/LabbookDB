import subprocess
import tempfile
import shutil
from string import Template
from sqlalchemy import create_engine, literal
from sqlalchemy.orm import relation, scoped_session, sessionmaker, eagerload, subqueryload, joinedload, lazyload, Load
from common_classes import *
from utils import get_script_dir
import pandas as pd
import os

tables = {"animals": Animal, "dna_extraction_protocols": DNAExtractionProtocol, "substances": Solution, "incubations": Incubation}

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

def make_document(my_header, my_content, my_footer):
	tex_document = my_header
	tex_document += my_content
	tex_document += my_footer
	return tex_document

def compose_instructions(table, code):

	#!!! for a system-wide install the location should likely be redefined!
	templates_path = os.path.join(get_script_dir(),"text_templates")

	# get dataframe with target protocol
	sql_query = session.query(tables[table]).options(Load(tables[table]).joinedload("*")).filter(tables[table].code == code)
	for item in sql_query:
		pass
	mystring = str(sql_query)
	mydf = pd.read_sql_query(mystring,engine,params=[code])
	print(mydf.columns)
	return

	template_keys = [i.split(table+"_")[1] for i in mydf.columns.tolist()]
	template_values = mydf.ix[0].tolist()

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

	# print mydf


	session.close()
	engine.dispose()

	# print(tex_document)
	return tex_document

def compose_PurificationProtocol(Protocol):
	tex_content = "\\begin{itemize}\n"
	return tex_content

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

	# p = Popen(["pdflatex"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	# grep_stdout = p.communicate(input=tex_document)[0]
	# if destination:
	# 	move("texput.pdf", destination)
	# all_files = os.listdir(".")
	# trace_files = [one_file for one_file in all_files if "texput" in one_file and ".pdf" not in one_file]
	# for trace_file in trace_files:
	# 	os.remove(trace_file)

if __name__ == '__main__':
	my_content=compose_instructions("dna_extraction_protocols","EPDqEP")
	# print_document(my_content, "lala.pdf")
	# tex_document = make_document(standard_header, my_content, standard_footer)
	# print_document(tex_document)
