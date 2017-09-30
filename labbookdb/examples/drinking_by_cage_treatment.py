from labbookdb.report.tracking import treatment_group, append_external_identifiers, qualitative_dates, cage_consumption
from labbookdb.report.selection import cage_periods, cage_drinking_measurements
from behaviopy.plotting import qualitative_times

db_path = '~/.demolog/meta.db'
df = cage_drinking_measurements(db_path, ['cFluDW'])
df = cage_consumption(db_path, df)

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
qualitative_times(df,
	x='qualitative_date',
	y='day_animal_consumption',
	unit='Cage_id',
	order=['ofM','ofMaF','ofMcF1','ofMcF2','ofMpF'],
	condition='TreatmentProtocol_code',
	err_style="boot_traces",
	save_as='drinking_by_cage_treatment.png'
	)
