from . import selection, formatting
from os import path
from behaviopy import plotting

def sucrose_preference(db_path, treatment_start_dates,
	bp_style=True,
	colorset=None,
	comparisons={"Period [days]":[]},
	compare="Treatment",
	rename_treatments={"cFluDW":"Fluoxetine","cFluDW_":"Control"},
	save_df="",
	):
	"""Plot sucrose preference scatterplot.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	treatment_start_dates : list
	A list containing the treatment start date or dates by which to filter the cages for the sucrose preference measurements.
	Items should be strings in datetime format, e.g. "2016,4,25,19,30".

	bp_style : bool, optional
	Whether to let behaviopy apply its default style.

	compare : string, optional
	Which parameter to categorize the comparison by. Must be a column name from df.

	comparisons : dict, optional
	A dictionary, the key of which indicates which df column to generate comparison insances from. If only a subset of the available rows are to be included in the comparison, the dictionary needs to specify a value, consisting of a list of acceptable values on the column given by the key.

	datacolumn_label : string, optional
	A column name from df, the values in which column give the data to plot.

	rename_treatments : dict, optional
	Dictionary specifying a rename scheme for the treatments. Keys are names to change and values are what to change the names to.

	save_df : string, optional
	Path under which to save the plotted dataframe. ".csv" will be appended to the string, and the data will be saved in CSV format.
	"""

	animals_df = selection.animals_by_cage_treatment(db_path, start_dates=treatment_start_dates)
	animals = list(set(animals_df["Animal_id"]))
	raw_df = selection.by_animals(db_path, "sucrose preference", animals=animals)
	full_df = animals_df.merge(raw_df, on="Animal_id", suffixes=("_Treatment",""))
	plottable_df = formatting.plottable_sucrosepreference_df(full_df)
	plotting.expandable_ttest(plottable_df,
		compare=compare,
		comparisons=comparisons,
		datacolumn_label="Sucrose Preference Ratio",
		rename_treatments=rename_treatments,
		colorset=colorset,
		)

	if save_df:
		df_path = path.abspath(path.expanduser(save_df))
		if not(df_path.endswith(".csv") or df_path.endswith(".CSV")):
			df_path += ".csv"
		plottable_df.to_csv(df_path)

	return plottable_df

def forced_swim(db_path, plot_style, treatment_start_dates,
	colorset=None,
	columns=["2 to 4"],
	rename_treatments={"cFluDW":"Fluoxetine","cFluDW_":"Control"},
	time_label="",
	plot_behaviour="immobility",
	save_df="",
	):
	"""Plot forced swim scatterplot.

	Parameters
	----------

	db_path : string
	Path to a LabbookDB formatted database.

	treatment_start_dates : list
	A list containing the treatment start date or dates by which to filter the cages for the sucrose preference measurements.
	Items should be strings in datetime format, e.g. "2016,4,25,19,30".

	rename_treatments : dict
	Dictionary specifying a rename scheme for the treatments. Keys are names to change and values are what to change the names to.

	save_df : string, optional
	Path under which to save the plotted dataframe. ".csv" will be appended to the string if not yet presenr, and the data will be saved in CSV format.
	"""

	raw_df = selection.parameterized(db_path, "forced swim", treatment_start_dates=treatment_start_dates)

	if plot_style in ["tsplot", "pointplot"]:
		if not time_label:
			time_label = "Interval [1 min]"
		if time_label == "Interval [1 min]":
			periods={1:[0,60],2:[60,120],3:[120,180],4:[180,240],5:[240,300],6:[300,360]}
			plottable_df = formatting.plottable_sums(raw_df, plot_behaviour, identifier_column="Animal_id", periods=periods, period_label=time_label)
		elif time_label == "Interval [2 min]":
			periods={1:[0,120],2:[120,240],3:[240,360]}
			plottable_df = formatting.plottable_sums(raw_df, plot_behaviour, identifier_column="Animal_id", periods=periods, period_label=time_label)
		if colorset:
			plotting.forced_swim_timecourse(plottable_df, legend_loc="best", rename_treatments=rename_treatments, time_label=time_label, plotstyle=plot_style, datacolumn_label="Immobility Ratio", colorset=colorset)
		else:
			plotting.forced_swim_timecourse(plottable_df, legend_loc="best", rename_treatments=rename_treatments, time_label=time_label, plotstyle=plot_style, datacolumn_label="Immobility Ratio")
	elif plot_style == "ttest":
		periods = {}
		for column_name in columns:
			start_minute, end_minute = column_name.split(" to ")
			start = int(start_minute)*60
			end = int(end_minute)*60
			periods[column_name] = [start,end]
		plottable_df = formatting.plottable_sums(raw_df, plot_behaviour, period_label="Interval [minutes]", periods=periods)
		if colorset:
			plotting.expandable_ttest(plottable_df, compare="Treatment", comparisons={"Interval [minutes]":[]}, datacolumn_label="Immobility Ratio", rename_treatments=rename_treatments, colorset=colorset)
		else:
			plotting.expandable_ttest(plottable_df, compare="Treatment", comparisons={"Interval [minutes]":[]}, datacolumn_label="Immobility Ratio", rename_treatments=rename_treatments)

	if save_df:
		df_path = path.abspath(path.expanduser(save_df))
		if not(df_path.endswith(".csv") or df_path.endswith(".CSV")):
			df_path += ".csv"
		plottable_df.to_csv(df_path)
