try:
	from ..report import selection, formatting
except (SystemError, ValueError):
	import selection, formatting
try:
	from ..db import query
except (ValueError, SystemError):
	import sys
	sys.path.append('/home/chymera/src/LabbookDB/labbookdb/db/')
	import query
if not __package__:
	import sys, os
	sys.path.append(os.path.expanduser('~/src/behaviopy'))
	sys.path.append(os.path.expanduser('~/src/timetableplot'))
from behaviopy import plotting
import ttp
import matplotlib.pyplot as plt
import behaviour
import selection
import tracking
import query

ALL_COHORT_START_DATES = ["2016,4,25,19,30","2016,5,19,23,5","2016,11,24,21,30","2017,1,31,22,0"]

def sucrose_preference(cohorts, compare):
	if cohorts == "cage":
		treatment_start_dates = ["2016,4,25,19,30","2016,5,19,23,5",]
	elif cohorts == "animal":
		treatment_start_dates = ["2016,11,24,21,30"]
	elif cohorts == "aileen_switching_sides":
		treatment_start_dates = ["2017,1,31,22,0"]
	elif cohorts == "all":
		treatment_start_dates = ALL_COHORT_START_DATES
	if compare == "treatment":
		behaviour.sucrose_preference(db_path, treatment_start_dates=treatment_start_dates, comparisons={"Period [days]":[]}, compare="Treatment",save_df="")
	elif compare == "side_preference":
		behaviour.sucrose_preference(db_path, treatment_start_dates=treatment_start_dates, comparisons={"Cage ID":[]}, compare="Sucrose Bottle Position", save_df="")

def timetable_plot(db_path):
	saturate = [
		{"Cage_TreatmentProtocol_code":["cFluDW","Cage_Treatment_start_date","Cage_Treatment_end_date"]},
		{"TreatmentProtocol_code":["aFluIV","Treatment_start_date"]},
		{"TreatmentProtocol_code":["aFluSC","Treatment_start_date"]}
		]

	col_entries=[
		("Animal","id"),
		("Treatment",),
		("FMRIMeasurement",),
		("TreatmentProtocol","code"),
		("Cage","id"),
		("Cage","Treatment",""),
		("Cage","TreatmentProtocol","code"),
		]
	join_entries=[
		("Animal.treatments",),
		("FMRIMeasurement",),
		("Treatment.protocol",),
		("Animal.cage_stays",),
		("CageStay.cage",),
		("Cage_Treatment","Cage.treatments"),
		("Cage_TreatmentProtocol","Cage_Treatment.protocol"),
		]
	filters = [["Cage_Treatment","start_date","2016,5,19,23,5"]]
	# filters = [["Cage_Treatment","start_date","2016,4,25,19,30"]]

	reference_df = query.get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=filters, outerjoin=True) # setting outerjoin to true will indirectly include controls
	ttp.multi_plot(reference_df, "Animal_id", shade=["FMRIMeasurement_date"], saturate=saturate)

if __name__ == '__main__':
	db_path="~/syncdata/meta.db"
	# forced_swim(db_path, "pointplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])
	# forced_swim(db_path, "pointplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"], period_label="interval [2 min]")

	timetable_plot(db_path)

	# sucrose_preference("animal", "treatment")
	# sucrose_preference("animal", "side_preference")

	# behaviour.forced_swim(db_path, "tsplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])
	# behaviour.forced_swim(db_path, "tsplot", treatment_start_dates=["2016,11,24,21,30"])
	# behaviour.forced_swim(db_path, "tsplot", treatment_start_dates=ALL_COHORT_START_DATES, save_df="")
	# behaviour.forced_swim(db_path, "pointplot", treatment_start_dates=ALL_COHORT_START_DATES, save_df="")

	# behaviour.forced_swim(db_path, "ttest", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"], columns=["2 to 4", "2 to 6"])
	# behaviour.forced_swim(db_path, "ttest", treatment_start_dates=["2016,11,24,21,30"], columns=["2 to 4", "2 to 6"])
	# behaviour.forced_swim(db_path, "ttest", treatment_start_dates=ALL_COHORT_START_DATES, columns=["2 to 4", "2 to 6"], save_df="")
	plt.show()
