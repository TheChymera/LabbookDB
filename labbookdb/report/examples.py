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

def get_animal_id_table(db_path,
	save_as=None,
	):
	import pandas as pd
	import os
	table = selection.data_selection(db_path, "animal ids")
	# print(table)
	table = table.pivot(index="AnimalExternalIdentifier_animal_id", columns='AnimalExternalIdentifier_database',)
	# table = table.pivot(index="AnimalExternalIdentifier_animal_id", columns='AnimalExternalIdentifier_database', values="AnimalExternalIdentifier_identifier","Animal_death_date")
	if save_as:
		table.to_html(os.path.abspath(os.path.expanduser(save_as)))
	else:
		# print(table.loc[:,[u'Animal_death_date',"ETH/AIC/cdb"]])
		# print(table[[u'Animal_death_date',u"AnimalExternalIdentifier_identifier"]])
		print(table)
		print(table.columns)

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
	get_animal_id_table(db_path)
	# get_animal_id_table(db_path,"~/animals.html")
