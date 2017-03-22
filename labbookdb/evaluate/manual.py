import os
import numpy as np

if not __package__:
	import sys, os
	sys.path.append(os.path.expanduser('~/src/behaviopy'))
from behaviopy import tracking

from labbookdb.db.query import get_df

def behaviour(db_path, test_type, animal_ids=[], animals_id_column="id_eth", dates=[], evaluations_dir="~/data/behaviour", author="", volume=0, random_order=True):
	"""Wrapper for evaluate() passing data from a LabbookDB model database.
	"""

	if not author:
		print("It is advisable to add your name's three-letter abbreviation via the \"author\" argument. This helps identify your work and protects it from being overwritten.")

	db_path = os.path.expanduser(db_path)
	evaluations_dir = os.path.expanduser(evaluations_dir)

	if test_type == "forced_swim_test":
		measurements_table = "ForcedSwimTestMeasurement"
		if os.path.basename(os.path.normpath(evaluations_dir)) != "forced_swim_test":
			evaluations_dir = os.path.join(evaluations_dir,"forced_swim_test")
		if not os.path.exists(evaluations_dir):
			os.makedirs(evaluations_dir)
		trial_duration = 360 #in seconds
		events = {"s":"swimming","i":"immobility"}
	else:
		raise ValueError("The function does not support test_type=\'"+test_type+"\'.")


	col_entries=[
		("Animal","id"),
		(measurements_table,),
		]
	join_entries=[
		("Animal.measurements",),
		(measurements_table,),
		]

	filters = []
	if animal_ids:
		filter_entry = ["Animal",animals_id_column]
		for animal_id in animal_ids:
			filter_entry.extend([animal_id])
		filters.append(filter_entry)
	if dates:
		filter_entry = ["measurements_table","date"]
		for date in dates:
			filter_entry.extend([date])
		filters.append(filter_entry)

	reference_df = get_df(db_path, col_entries=col_entries, join_entries=join_entries, filters=filters)
	if random_order:
		reference_df = reference_df.iloc[np.random.permutation(len(reference_df))]

	for _, measurement_df in reference_df.iterrows():
		recording_path = measurement_df.loc[measurements_table+"_recording"]
		if measurements_table+"_recording_bracket" in reference_df.columns:
			bracket = measurement_df.loc[measurements_table+"_recording_bracket"]
		else:
			bracket = ""
		outfile_name = os.path.splitext(os.path.basename(recording_path))[0]+"_"+bracket+"_"+author
		output_path = os.path.join(evaluations_dir,outfile_name)
		tracking.manual_events(recording_path,trial_duration,events=events,bracket=bracket, volume=volume, output_path=output_path)

if __name__ == '__main__':
	behaviour("~/syncdata/meta.db","forced_swim_test",animal_ids=[],author="chr",volume=0.1)
