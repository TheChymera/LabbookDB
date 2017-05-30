import codecs
import sadisplay
import pydotplus
from labbookdb.db.query import ALLOWED_CLASSES

def generate_schema(
	extent="all",
	save_dotfile="",
	save_plot="",
	):
	"""Retreive the LabbookDB schema and save either a DOT file, or a PNG plot
	"""

	if extent == "all":
		desc = sadisplay.describe(ALLOWED_CLASSES.values())
	elif type(extent) is list:
		desc = sadisplay.describe([ALLOWED_CLASSES[key] for key in extent])

	if save_dotfile:
		with codecs.open(save_dotfile, 'w', encoding='utf-8') as f:
			f.write(sadisplay.dot(desc))

	if save_plot:
		graph = pydotplus.graph_from_dot_data(sadisplay.dot(desc))
		graph.write_png(save_plot)

if __name__ == '__main__':
	generate_schema(extent="all")
	# generate_schema(extent=["Animal","CageStay","Cage","Genotype","OpenFieldTestMeasurement","FMRIMeasurement"])
	# generate_schema(extent=["Animal","CageStay","Cage"])
