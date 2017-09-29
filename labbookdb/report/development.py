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

def drinking_water_by_cage_treatment(
	treatment_relative_date=True,
	rounding='D',
	):
	from labbookdb.report.tracking import treatment_group, append_external_identifiers
	from labbookdb.report.selection import cage_periods, cage_water_consumption_and_occupancy

	DB_PATH = '~/syncdata/meta.db'
	df = cage_water_consumption_and_occupancy(DB_PATH,['cFluDW_'])
	selected_cages = list(df['Cage_id'].unique())
	occupancy_df = cage_periods(DB_PATH, cage_filter=selected_cages)
	df['occupancy']=''
	for measurement in df['DrinkingMeasurement_id'].tolist():
		selection = df[df['DrinkingMeasurement_id']==measurement]
		measurement_start = selection['DrinkingMeasurement_reference_date'].values[0]
		measurement_end = selection['DrinkingMeasurement_date'].values[0]
		cage_id = selection['Cage_id'].values[0]
		occupants = occupancy_df[
				(occupancy_df['CageStay_start_date']<=measurement_start)&
				(
					(occupancy_df['CageStay_end_date']>=measurement_end)|
					(occupancy_df['CageStay_end_date'].isnull())
				)&
				(occupancy_df['Cage_id']==cage_id)
				]
		if True in occupants['Animal_id'].duplicated().tolist():
			print(occupants)
			raise ValueError('An animal ist listed twice in the occupancy list of a cage (printed above). This biases the occupancy evaluation, and is likely diagnostic of a broader processing error.')
		occupancy = len(occupants.index)
		df.loc[(df['DrinkingMeasurement_id']==measurement),'occupancy'] = occupancy
	if treatment_relative_date:
		df['relative_start_date'] = ''
		df['relative_end_date'] = ''
		df['relative_start_date'] = df['relative_start_date'].astype('timedelta64[ns]')
		df['relative_end_date'] = df['relative_end_date'].astype('timedelta64[ns]')
		df["relative_start_date"] = df["DrinkingMeasurement_reference_date"]-df["Treatment_start_date"]
		df["relative_end_date"] = df["DrinkingMeasurement_date"]-df["Treatment_start_date"]
	if rounding:
                df['relative_start_date'] = df['relative_start_date'].dt.round(rounding)
                df['relative_end_date'] = df['relative_end_date'].dt.round(rounding)
	print(df)
