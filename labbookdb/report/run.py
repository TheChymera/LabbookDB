import selection, formatting
if not __package__:
	import sys, os
	sys.path.append(os.path.expanduser('~/src/behaviopy'))
from behaviopy import plotting

def sucrose_prefernce():
	raw_df = selection.sucrose_prefernce()
	plottable_df = formatting.plottable_sucrosepreference_df(raw_df)
	plotting.sucrose_preference(plottable_df, plot_columns=["0 to 2", "2 to 5"],legend_loc=4, rename_treatments={"cFluDW":"Fluoxetine","cFluDW_":"Control"})

if __name__ == '__main__':
	sucrose_prefernce()
