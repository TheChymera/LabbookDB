if __package__ is None:
	import sys
	sys.path.append('/home/chymera/src/LabbookDB/')
	import labbookdb.report
	__package__ = "labbookdb.report.selection"
from ...db import query

def sucrose_prefernce(db_path, treatment_start_dates=[]):
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
	if treatment_start_dates:
		my_filter = ["Treatment","start_date"]
		my_filter.extend(treatment_start_dates)
	else:
		my_filter = None
	df = query.get_df(db_path,col_entries=col_entries, join_entries=join_entries, filters=[my_filter])

	return df

if __name__ == '__main__' and __package__ is None:
	sucrose_prefernce()
