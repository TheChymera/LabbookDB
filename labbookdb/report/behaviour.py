try:
	from ..report import selection, formatting
except (SystemError, ValueError):
	import selection, formatting
if not __package__:
	import sys, os
	sys.path.append(os.path.expanduser('~/src/behaviopy'))
from behaviopy import plotting
import matplotlib.pyplot as plt

def sucrose_preference(db_path, treatment_start_dates,
	columns=[],
	rename_treatments={"cFluDW":"Fluoxetine","cFluDW_":"Control"},
	):
	"""Plot sucrose preference scatterplot.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	treatment_start_dates : list
	A list containing the treatment start date or dates by which to filter the cages for the sucrose preference measurements.
	Items should be strings in datetime format, e.g. "2016,4,25,19,30".

	columns : list, optional
	Which sucrose preference data columns to plot, values can be "0 to 2" and "2 to 5"

	rename_treatments : dict, optional
	Dictionary specifying a rename scheme for the treatments. Keys are names to change and values are what to change the names to.
	"""

	animals_df = selection.animals_by_cage_treatment(db_path, start_dates=treatment_start_dates)
	animals = list(set(animals_df["Animal_id"]))
	raw_df = selection.by_animals(db_path, "sucrose preference", animals=animals)
	full_df = animals_df.merge(raw_df, on="Animal_id", suffixes=("_Treatment",""))
	plottable_df = formatting.plottable_sucrosepreference_df(full_df)
	print(plottable_df)
	plotting.sucrose_preference(plottable_df, legend_loc=4, columns=columns, rename_treatments=rename_treatments)

def forced_swim(db_path, plot_style, treatment_start_dates,
	columns=["2 to 4"],
	rename_treatments={"cFluDW":"Fluoxetine","cFluDW_":"Control"},
	period_label="",
	plot_behaviour="immobility",
	):
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

	raw_df = selection.data_selection(db_path, "forced swim", treatment_start_dates=treatment_start_dates)

	if plot_style in ["tsplot", "pointplot"]:
		if not period_label:
			period_label = "interval [1 min]"
		if period_label == "interval [1 min]":
			periods={1:[0,60],2:[60,120],3:[120,180],4:[180,240],5:[240,300],6:[300,360]}
			plottable_df = formatting.plottable_sums(raw_df, plot_behaviour, identifier_column="Animal_id", periods=periods, period_label=period_label)
		elif period_label == "interval [2 min]":
			periods={1:[0,120],2:[120,240],3:[240,360]}
			plottable_df = formatting.plottable_sums(raw_df, plot_behaviour, identifier_column="Animal_id", periods=periods, period_label=period_label)
		plotting.forced_swim_timecourse(plottable_df, legend_loc="best", rename_treatments=rename_treatments, period_label=period_label, plotstyle=plot_style, plot_behaviour=plot_behaviour)
	elif plot_style == "ttest":
		periods = {}
		for column_name in columns:
			start_minute, end_minute = column_name.split(" to ")
			start = int(start_minute)*60
			end = int(end_minute)*60
			periods[column_name] = [start,end]
		plottable_df = formatting.plottable_sums(raw_df, plot_behaviour, period_label="interval [minutes]", periods=periods)
		plotting.forced_swim_ttest(plottable_df, legend_loc=4, periods=periods, rename_treatments=rename_treatments)
