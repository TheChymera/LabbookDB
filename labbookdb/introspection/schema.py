import codecs
import sadisplay
import pydotplus
from labbookdb.db.query import ALLOWED_CLASSES

def generate_schema(extent="all"):
	if extent == "all":
		desc = sadisplay.describe(ALLOWED_CLASSES.values())
	elif type(extent) is list:
		desc = sadisplay.describe([ALLOWED_CLASSES[key] for key in extent])

	with codecs.open('schema.dot', 'w', encoding='utf-8') as f:
		f.write(sadisplay.dot(desc))

	graph = pydotplus.graph_from_dot_data(sadisplay.dot(desc))
	# (graph,) = pydotplus.graph_from_dot_data(sadisplay.dot(desc))
	graph.write_png('somefile.png')

if __name__ == '__main__':
	generate_schema(extent="all")
	# generate_schema(extent=["Animal","CageStay","Cage","Genotype","OpenFieldTestMeasurement","FMRIMeasurement"])
	# generate_schema(extent=["Animal","CageStay","Cage"])
