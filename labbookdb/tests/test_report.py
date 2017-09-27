import pytest

def test_groups():
	"""Create a `pandas.DataFrame` containing treatment and genotype group assignments"""
	from labbookdb.report.tracking import treatment_group, append_external_identifiers

	db_path = '~/syncdata/meta.db'

	df = treatment_group(db_path, ['cFluDW','cFluDW_'], 'cage')
	df = append_external_identifiers(db_path, df, ['Genotype_code'])
