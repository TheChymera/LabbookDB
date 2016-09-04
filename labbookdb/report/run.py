import selection, formatting
if not __package__:
	import sys, os
	sys.path.append(os.path.expanduser('~/src/behaviopy'))
from behaviopy import plotting

db_path="~/syncdata/meta.db"

def sucrose_prefernce(db_path, treatment_start_dates, plot_columns=["0 to 2", "2 to 5"], rename_treatments={"cFluDW":"Fluoxetine","cFluDW_":"Control"}):
	"""Plot sucrose preference scatterplot.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	treatment_start_dates : list
	A list containing the treatment start date or dates by which to filter the cages for the sucrose preference measurements.
	Items should be strings in datetime format, e.g. "2016,4,25,19,30".

	plot_columns : list
	Which sucrose preference data columns to plot, values can be "0 to 2" and "2 to 5"

	rename_treatments : dict
	Dictionary specifying a rename scheme for the treatments. Keys are names to change and values are what to change the names to.
	"""

	raw_df = selection.sucrose_prefernce(db_path, treatment_start_dates=treatment_start_dates)
	plottable_df = formatting.plottable_sucrosepreference_df(raw_df)
	plotting.sucrose_preference(plottable_df, plot_columns=plot_columns, legend_loc=4, rename_treatments=rename_treatments)

if __name__ == '__main__':
	sucrose_prefernce(db_path, treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])
