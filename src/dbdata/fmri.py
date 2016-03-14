from subprocess import Popen, PIPE, STDOUT, call
from shutil import move
from sqlalchemy import create_engine, literal
from common_classes import *
from utils import get_script_dir
import pandas as pd
import os

tables = {"animals": Animal, "dna_extraction_protocols": DNAExtractionProtocol}

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

	tex_content = "\\begin{itemize}\n"

	#!!! for a system-wide install the location should likely be redefined!
	templates_path = os.path.join(get_script_dir(),"text_templates")

	with open(os.path.join(templates_path,'standard_header.tex'), 'r') as myfile:
		standard_header=myfile.read()
	with open(os.path.join(templates_path,'standard_footer.tex'), 'r') as myfile:
		standard_footer=myfile.read()
	with open(os.path.join(templates_path,table+'.tex'), 'r') as myfile:
		tex_content=myfile.read()

	tex_document = standard_header
	tex_document += tex_content
	tex_document += standard_footer

	sql_query = session.query(tables[table]).order_by(tables[table].code)
	for item in sql_query:
		pass
	mystring = str(sql_query)
	mydf = pd.read_sql_query(mystring,engine)
	# print mydf


	session.close()
	engine.dispose()

	print(tex_document)
	return tex_document

def compose_PurificationProtocol(Protocol):
	tex_content = "\\begin{itemize}\n"
	return tex_content

def print_document(tex_document, destination=None):
	p = Popen(["pdflatex"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	grep_stdout = p.communicate(input=tex_document)[0]
	if destination:
		move("texput.pdf", destination)
	all_files = os.listdir(".")
	trace_files = [one_file for one_file in all_files if "texput" in one_file and ".pdf" not in one_file]
	for trace_file in trace_files:
		os.remove(trace_file)

if __name__ == '__main__':
	my_content=compose_instructions("dna_extraction_protocols","EPDqEP")
	# tex_document = make_document(standard_header, my_content, standard_footer)
	# print_document(tex_document)
