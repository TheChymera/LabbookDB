def animal_weights():
	import matplotlib.pyplot as mpl
	from labbookdb.report.tracking import animal_weights
	from behaviopy.plotting import weights

	qualitative_times = {
			"ofM":[-14,-15,-13,-7,-8,-6],
			"ofMaF":[0,-1],
			"ofMcF1":[14,13,15],
			"ofMcF2":[28,27,29],
			"ofMpF":[45,44,46],
		}

	df = animal_weights('~/syncdata/meta.db', {'animal':['aFluIV','aFluIV_']})
	df['relative_date'] = df['relative_date'].dt.days.astype(int)
	df = df[['Animal_id', 'relative_date', 'weight', 'TreatmentProtocol_code', 'ETH/AIC']]
	df['qualitative_date']=""
	for subject in df['Animal_id']:
		try:
			for label, dates in qualitative_times.iteritems():
				for date in dates:
					if date in df[df["Animal_id"]==subject]["relative_date"]:
						print("lala")
						break
		except AttributeError:
			for label, dates in qualitative_times.items():
				for date in dates:
					if date in df[df["Animal_id"]==subject]["relative_date"].values:
						df.loc[(df["Animal_id"]==subject)&(df["relative_date"]==date),'qualitative_date']=label
						break

	weights(df, order=['ofM','ofMaF','ofMcF1','ofMcF2','ofMpF'], condition='TreatmentProtocol_code', err_style="boot_traces", time='qualitative_date')
	df = df[df['qualitative_date']=='ofMpF']
	print(df)
	mpl.show()
