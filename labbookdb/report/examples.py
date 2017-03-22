try:
	from ..report import selection, formatting
except (SystemError, ValueError):
	import selection, formatting
if not __package__:
	import sys, os
	sys.path.append(os.path.expanduser('~/src/behaviopy'))
from behaviopy import plotting
import matplotlib.pyplot as plt
import behaviour
import selection
import tracking
import query

ALL_COHORT_START_DATES = ["2016,4,25,19,30","2016,5,19,23,5","2016,11,24,21,30"]

def sucrose_preference(measurement_mode):
	if measurement_mode == "cage":
		behaviour.sucrose_preference(db_path, treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5",])
	elif measurement_mode == "animal":
		behaviour.sucrose_preference(db_path, treatment_start_dates=["2016,11,24,21,30"])
	elif measurement_mode == "any":
		behaviour.sucrose_preference(db_path, treatment_start_dates=ALL_COHORT_START_DATES)


if __name__ == '__main__':
	db_path="~/syncdata/meta.db"
	# forced_swim(db_path, "pointplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])
	# forced_swim(db_path, "pointplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"], period_label="interval [2 min]")

	sucrose_preference("cage")

	# behaviour.forced_swim(db_path, "tsplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])
	# behaviour.forced_swim(db_path, "tsplot", treatment_start_dates=["2016,11,24,21,30"])
	# behaviour.forced_swim(db_path, "tsplot", treatment_start_dates=ALL_COHORT_START_DATES)

	# behaviour.forced_swim(db_path, "ttest", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"], columns=["2 to 4", "2 to 6"])
	# behaviour.forced_swim(db_path, "ttest", treatment_start_dates=["2016,11,24,21,30"], columns=["2 to 4", "2 to 6"])
	# behaviour.forced_swim(db_path, "ttest", treatment_start_dates=ALL_COHORT_START_DATES, columns=["2 to 4", "2 to 6"])
	plt.show()
