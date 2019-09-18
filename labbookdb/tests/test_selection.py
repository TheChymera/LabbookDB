import pytest
from os import path

DB_PATH = '~/.demolog/meta.db'
DATA_DIR = path.join(path.dirname(path.realpath(__file__)),'../../example_data/')

def test_parameterized_animals_base():
	import numpy as np
	import pandas as pd
	from labbookdb.report.selection import animal_id, parameterized
	from datetime import datetime

	db_path=DB_PATH
	animal = animal_id(db_path,'ETH/AIC','5684')
	info_df = parameterized(db_path, 'animals base', animal_filter=[animal])

	birth = datetime(2016, 7, 21)

	assert info_df['Animal_sex'].item() == 'm'
	assert info_df['Animal_birth_date'][0] == birth
