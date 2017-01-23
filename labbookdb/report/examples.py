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

if __name__ == '__main__':
	db_path="~/syncdata/meta.db"
	# sucrose_preference(db_path, treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])
	# forced_swim(db_path, "ttest", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"], columns=["2 to 4", "2 to 6"])
	# behaviour.forced_swim(db_path, "tsplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])
	# forced_swim(db_path, "pointplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])
	# forced_swim(db_path, "pointplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"], period_label="interval [2 min]")
	# forced_swim(db_path, "tsplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"], period_label="interval [2 min]")
	# plt.show()
	# print(table)
	# tracking.animal_id_table(db_path)
	tracking.animal_id_table(db_path,"~/animals.html")
