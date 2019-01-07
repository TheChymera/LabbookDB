
def animal_multiselect(
	cage_treatments=['cFluDW','cFluDW_']
	):
	from labbookdb.report.selection import animal_id, animal_treatments, animal_operations

	db_path='~/syncdata/meta.db'
	df_treatments = animal_treatments(db_path, cage_treatments=cage_treatments)['Animal_id'].tolist()
	df_implants = animal_operations(db_path, implant_targets=['dr_impl'])['Animal_id'].tolist()
	df_virus = animal_operations(db_path, virus_targets=['dr_skull','dr_dura','dr_dura_shallow','dr_skull_perpendicular'])['Animal_id'].tolist()
	df_treatments = [animal_id(db_path, 'ETH/AIC', i, reverse=True) for i in df_treatments]
	df_implants = [animal_id(db_path, 'ETH/AIC', i, reverse=True) for i in df_implants]
	df_virus = [animal_id(db_path, 'ETH/AIC', i, reverse=True) for i in df_virus]
	d = [df_treatments, df_implants, df_virus]
	selection = list(set(d[0]).intersection(*d))
	return selection

def animal_weights_():
	import matplotlib.pyplot as mpl
	from labbookdb.report.tracking import animal_weights, qualitative_dates
	from behaviopy.plotting import qualitative_times

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
	qualitative_times(df, order=['ofM','ofMaF','ofMcF1','ofMcF2','ofMpF'], condition='TreatmentProtocol_code', err_style="boot_traces", time='qualitative_date')
	df = df[df['qualitative_date']=='ofMpF']
	print(df)
	mpl.show()

def drinking_water_by_cage_treatment(
	treatment_relative_date=True,
	rounding='D',
	):
	from labbookdb.report.tracking import treatment_group, append_external_identifiers, qualitative_dates, cage_consumption
	from labbookdb.report.selection import cage_periods, cage_drinking_measurements
	from behaviopy.plotting import weights
	import matplotlib.pyplot as plt


	DB_PATH = '~/syncdata/meta.db'
	df = cage_drinking_measurements(DB_PATH,['cFluDW','cFluDW_'])
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
	weights(df,
		weight='day_animal_consumption',
		unit='Cage_id',
		order=['ofM','ofMaF','ofMcF1','ofMcF2','ofMpF'],
		condition='TreatmentProtocol_code',
		err_style="boot_traces",
		time='qualitative_date',
		)
	plt.show()
