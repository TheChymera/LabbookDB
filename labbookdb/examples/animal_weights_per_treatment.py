from labbookdb.report.tracking import animal_weights, qualitative_dates
from behaviopy.plotting import weights

fuzzy_matching = {
		"ofM":[-14,-15,-13,-7,-8,-6],
		"ofMaF":[0,-1],
		"ofMcF1":[14,13,15],
		"ofMcF2":[28,27,29],
		"ofMpF":[45,44,46],
	}

df = animal_weights('~/.demolog/meta.db', {'cage':['cFluDW','cFluDW_']})
df['relative_date'] = df['relative_date'].dt.days.astype(int)
df = df[['Animal_id', 'relative_date', 'weight', 'Cage_TreatmentProtocol_code', 'ETH/AIC']]
df = qualitative_dates(df, fuzzy_matching=fuzzy_matching)
qualitative_times(df,
	order=['ofM','ofMaF','ofMcF1','ofMcF2','ofMpF'],
	condition='Cage_TreatmentProtocol_code',
	err_style="boot_traces",
	time='qualitative_date',
	save_as='animal_weights_per_treatment.png',
	)
