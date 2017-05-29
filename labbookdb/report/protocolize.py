import os
import shutil
import subprocess
import tempfile
import pandas as pd
from string import Template
from sqlalchemy import create_engine, literal, inspection
from sqlalchemy.orm import aliased, relation, scoped_session, sessionmaker, eagerload, subqueryload, joinedload, lazyload, Load
from ..db.common_classes import *
from ..db.query import get_for_protocolize


from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

def compose_tex(db_path, class_name, code):
	"""Create a TeX document containing the protocol of the class_name entry identified by a given code.
	"""

	#!!! for a system-wide install the location should likely be redefined!
	thisscriptspath = os.path.dirname(os.path.realpath(__file__))
	templates_path = os.path.join(thisscriptspath,"text_templates")

	mydf = get_for_protocolize(db_path, class_name, code)

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
	with open(os.path.join(templates_path,class_name+'.tex'), 'r') as myfile:
		template_file=myfile.read()
		tex_template=Template(template_file)
		tex_template = tex_template.substitute(templating_dictionary)

	tex_document = standard_header
	tex_document += tex_template
	tex_document += standard_footer

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
