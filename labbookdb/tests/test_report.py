import pytest

DB_PATH = '~/.demolog/meta.db'

def test_groups():
	"""Create a `pandas.DataFrame` containing treatment and genotype group assignments"""
	from labbookdb.report.tracking import treatment_group, append_external_identifiers

	known_sorted_ids = ['5667', '5668', '5673', '5674', '5675', '5689', '5690', '5691', '5692', '5693', '5694', '5694', '5699', '5700', '5704', '5705', '5706', '6254', '6256', '6262']

	df = treatment_group(DB_PATH, ['cFluDW','cFluDW_'], 'cage')
	df = append_external_identifiers(DB_PATH, df, ['Genotype_code'])
	sorted_ids = sorted(df['ETH/AIC'].tolist())

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
