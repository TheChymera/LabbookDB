import pytest

def test_groups():
	"""Create a `pandas.DataFrame` containing treatment and genotype group assignments"""
	from labbookdb.report.tracking import treatment_group, append_external_identifiers

	known_sorted_ids = ['5667', '5668', '5673', '5674', '5675', '5689', '5690', '5691', '5692', '5693', '5694', '5694', '5699', '5700', '5704', '5705', '5706', '6254', '6255', '6256', '6262']

	db_path = '~/.demolog/meta.db'
	df = treatment_group(db_path, ['cFluDW','cFluDW_'], 'cage')
	df = append_external_identifiers(db_path, df, ['Genotype_code'])
	sorted_ids = sorted(df['ETH/AIC'].tolist())

	assert sorted_ids == known_sorted_ids
