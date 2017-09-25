def animal_weights():
	import matplotlib.pyplot as mpl
	from labbookdb.report.tracking import animal_weights, qualitative_dates
	from behaviopy.plotting import weights

	fuzzy_matching = {
			"ofM":[-14,-15,-13,-7,-8,-6],
			"ofMaF":[0,-1],
			"ofMcF1":[14,13,15],
			"ofMcF2":[28,27,29],
			"ofMpF":[45,44,46],
		}

	df = animal_weights('~/syncdata/meta.db', {'cage':['cFluDW','cFluDW_']})
	df['relative_date'] = df['relative_date'].dt.days.astype(int)
	df = df[['Animal_id', 'relative_date', 'weight', 'Cage_TreatmentProtocol_code', 'ETH/AIC']]
	df = qualitative_dates(df, fuzzy_matching=fuzzy_matching)
	weights(df, order=['ofM','ofMaF','ofMcF1','ofMcF2','ofMpF'], condition='Cage_TreatmentProtocol_code', err_style="boot_traces", time='qualitative_date')
	df = df[df['qualitative_date']=='ofMpF']
	print(df)
	mpl.show()

def animal_weights_():
	import matplotlib.pyplot as mpl
	from labbookdb.report.tracking import animal_weights, qualitative_dates
	from behaviopy.plotting import weights

	fuzzy_matching = {
			"ofM":[-14,-15,-13,-7,-8,-6],
			"ofMaF":[0,-1],
			"ofMcF1":[14,13,15],
			"ofMcF2":[28,27,29],
			"ofMpF":[45,44,46],
		}

	df = animal_weights('~/syncdata/meta.db', {'animal':['aFluIV','aFluIV_']})
	df['relative_date'] = df['relative_date'].dt.days.astype(int)
	df = df[['Animal_id', 'relative_date', 'weight', 'TreatmentProtocol_code', 'ETH/AIC']]
	df = qualitative_dates(df, fuzzy_matching=fuzzy_matching)
	weights(df, order=['ofM','ofMaF','ofMcF1','ofMcF2','ofMpF'], condition='TreatmentProtocol_code', err_style="boot_traces", time='qualitative_date')
	df = df[df['qualitative_date']=='ofMpF']
	print(df)
	mpl.show()

def group():
	from labbookdb.report.tracking import treatment_group
	from labbookdb.report import selection
	from labbookdb.report.utilities import make_identifier_short_form, collapse_rename


	db_path = '~/syncdata/meta.db'

	df1 = treatment_group(db_path, ['cFluDW','cFluDW_'], 'cage')

        df = selection.parameterized(db_path, "animals info")

        collapse = {
                'Animal_death_date' : lambda x: ', '.join(set([str(i) for i in x])),
                }
        short_identifiers = make_identifier_short_form(df)
        df = short_identifiers.join(collapse_rename(df, 'AnimalExternalIdentifier_animal_id', collapse))
        df.reset_index().set_index('Animal_id', inplace=True)
	print(df)
	print(df1)
