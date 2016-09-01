from ..db import query

def sucrose_prefernce():
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
	filters = [["Treatment","start_date","2016,4,25,19,30","2016,5,19,23,5"]]
	reference_df = get_df("~/syncdata/meta.db",col_entries=col_entries, join_entries=join_entries, filters=filters)

if __name__ == '__main__':
	sucrose_prefernce()
