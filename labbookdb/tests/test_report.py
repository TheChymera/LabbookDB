import pytest
from os import path

DB_PATH = '~/.demolog/meta.db'
DATA_DIR = path.join(path.dirname(path.realpath(__file__)),'../../example_data/')

def test_bids_eventsfile():
	"""Check if correct BIDS events file can be sourced."""
	from labbookdb.report.tracking import bids_eventfile
	import pandas as pd

	df = bids_eventfile(DB_PATH,'chr_longSOA')
	bids_eventsfile = path.join(DATA_DIR,'bids_eventsfile.csv')
	df_ = pd.read_csv(bids_eventsfile, index_col=0)
	assert df[['onset','duration']].equals(df_[['onset','duration']])

def test_groups():
	"""Create a `pandas.DataFrame` containing treatment and genotype group assignments"""
	from labbookdb.report.tracking import treatment_group, append_external_identifiers

	known_sorted_ids = ['5667', '5668', '5673', '5674', '5675', '5689', '5690', '5691', '5692', '5693', '5694', '5694', '5699', '5700', '5704', '5705', '5706', '6254', '6256', '6262']

	df = treatment_group(DB_PATH, ['cFluDW','cFluDW_'], level='cage')
	df = append_external_identifiers(DB_PATH, df, ['Genotype_code'])
	sorted_ids = sorted(df['ETH/AIC'].tolist())

	print(df['ETH/AIC'].tolist(),sorted_ids,known_sorted_ids)
	assert sorted_ids == known_sorted_ids

def test_animal_cage_treatment_control_in_report():
	"""Check if animal which died before the cagetreatment was applied to its last home cage is indeed not showing a cage treatment, but still showing the animal treatment."""
	from labbookdb.report.tracking import animals_info

	df = animals_info(DB_PATH,
		save_as=None,
		functional_scan_responders=True,
		treatments=True,
		)
	assert df[df['ETH/AIC']=='6255']['cage_treatment'].values[0] == ""
	assert df[df['ETH/AIC']=='6255']['animal_treatment'].values[0] == 'aFluIV_'

def test_drinking_by_cage_treatment(
	treatment_relative_date=True,
	rounding='D',
	):
	from labbookdb.report.tracking import treatment_group, append_external_identifiers, qualitative_dates, cage_consumption
	from labbookdb.report.selection import cage_periods, cage_drinking_measurements

	known_cage_ids = [25, 38, 41]
	known_consumption_values = [2.35, 2.51, 2.94, 2.95, 3.16, 3.17, 3.22, 3.23, 3.24, 3.25, 3.49, 3.63, 3.72, 4.04, 4.09, 4.58, 4.98, 5.15, 5.31, 5.39, 5.54, 5.97, 6.73, 6.78]

	df = cage_drinking_measurements(DB_PATH,['cFluDW'])
	df = cage_consumption(DB_PATH,df)

	fuzzy_matching = {
		"ofM":[-14,-15,-13,-7,-8,-6],
		"ofMaF":[0,-1],
		"ofMcF1":[14,13,15],
		"ofMcF2":[28,27,29],
		"ofMpF":[45,44,46,43,47],
	}
	df = qualitative_dates(df,
		iterator_column='Cage_id',
		date_column='relative_end_date',
		label='qualitative_date',
		fuzzy_matching=fuzzy_matching,
		)

	cage_ids = sorted(df['Cage_id'].unique())
	assert cage_ids == known_cage_ids

	consumption_values = df['day_animal_consumption'].values
	consumption_values = [round(i, 2) for i in consumption_values]
	consumption_values = sorted(list(set(consumption_values)))
	assert consumption_values == known_consumption_values
