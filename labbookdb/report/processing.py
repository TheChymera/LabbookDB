import pandas as pd

def timedelta_sums(evaluation_path, index_name="", period_start=False, period_end=False):
	"""Return the per-behaviour sums of timedelta intervals.

	Parameters
	----------

	timedelta_df : pandas_dataframe
		A pandas dataframe containing a "behaviour" and a "timedelta" column
	index_name : string, optional
		The name to add as an index of the retunred series (useful for concatenating multiple outputs)
	period_start : float, optional
		The timepoint at which the evaluation period for the timedelta sums starts.
	period_end : float, optional
		The timepoint at which the evaluation period for the timedelta sums ends.
	"""

	timedelta_df = timedeltas(evaluation_path, period_start=period_start, period_end=period_end)
	sums = {}
	for behaviour in list(set(timedelta_df["behaviour"])):
		sums[behaviour] = timedelta_df.loc[timedelta_df["behaviour"] == behaviour, "timedelta"].sum()
	sum_df = pd.DataFrame(sums, index=[index_name])
	return sum_df

def timedeltas(evaluation_path, period_start=False, period_end=False):
	"""Return per-behaviour timedelta intervals.

	Parameters
	----------

	timedelta_df : pandas_dataframe
		A pandas dataframe containing a "behaviour" and a "start" column
	period_start : float, optional
		The timepoint at which the evaluation period for the timedelta starts.
	period_end : float, optional
		The timepoint at which the evaluation period for the timedelta ends.
	"""

	df = pd.read_csv(evaluation_path)

	#edit df to fit restricted summary period
	if period_start:
		cropped_df = df[df["start"] > period_start]
		# we perform this check so that the period is not extended beyond the data range
		if not len(cropped_df) == len(df):
			startpoint_behaviour = list(df[df["start"] <= period_start].tail(1)["behaviour"])[0]
			startpoint = pd.DataFrame({"start":period_start,"behaviour":startpoint_behaviour}, index=[""])
			df = pd.concat([startpoint,cropped_df])
	if period_end:
		cropped_df = df[df["start"] < period_end]
		# we perform this check so that the period is not extended beyond the data range
		if not len(cropped_df) == len(df):
			endpoint = pd.DataFrame({"start":period_end,"behaviour":"ANALYSIS_ENDPOINT"}, index=[""])
			df = pd.concat([cropped_df,endpoint])

	# timedelta calculation
	df["timedelta"] = (df["start"].shift(-1)-df["start"]).fillna(0)

	#the last index gives the experiment end time, not meaningful behaviour. We remove that here.
	df = df[:-1]

	return df

def rounded_days(datetime_obj):
	days = datetime_obj.days
	# rounding number of days up, as timedelta.days returns the floor only:
	if datetime_obj.seconds / 43199.5 >= 1:
		days += 1
	return days
