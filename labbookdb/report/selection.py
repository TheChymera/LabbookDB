if __package__ is None:
	import sys, os
	pkg_root = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"../.."))+"/"
	sys.path.append(pkg_root)
	import labbookdb.report
	__package__ = "labbookdb.report.selection"
from ...db import query

def data_selection(db_path, data_type, treatment_start_dates=[]):
	"""Select dataframe from a LabbookDB style database.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	data_type : string
	What type of data should be selected values can be:
		"sucrose preference"
		"forced swim"

	treatment_start_dates : list, optional
	A list containing the treatment start date or dates by which to filter the cages for the sucrose preference measurements.
	Items should be strings in datetime format, e.g. "2016,4,25,19,30".
	"""
	if data_type == "sucrose preference":
		col_entries=[
			("Cage","id"),
			("Treatment",),
			("SucrosePreferenceMeasurement",),
			("TreatmentProtocol","code"),
			]
		join_entries=[
			("Cage.treatments",),
			("SucrosePreferenceMeasurement",),
			("Treatment.protocol",),
			]
	elif data_type == "forced swim":
		col_entries=[
			("Animal","id"),
			("Cage","id"),
			("Treatment",),
			("TreatmentProtocol","code"),
			("ForcedSwimTestMeasurement",),
			("Evaluation",),
			]
		join_entries=[
			("Animal.cage_stays",),
			("ForcedSwimTestMeasurement",),
			("Evaluation",),
			("CageStay.cage",),
			("Cage.treatments",),
			("Treatment.protocol",),
			]

	if treatment_start_dates:
		my_filter = ["Treatment","start_date"]
		my_filter.extend(treatment_start_dates)
	else:
		my_filter = None
	df = query.get_df(db_path,col_entries=col_entries, join_entries=join_entries, filters=[my_filter])

	return df

if __name__ == '__main__' and __package__ is None:
	sucrose_prefernce()
