import pandas as pd
try:
	from ..report import processing
except SystemError:
	import processing

def plottable_sums(reference_df, behaviour, identifier_column="Animal_id", periods={}, period_label="period", metadata_columns={"TreatmentProtocol_code":"treatment"}):
	identifiers = list(set(reference_df[identifier_column]))
	evaluation_df = pd.DataFrame({})
	for identifier in identifiers:
		identifier_df = reference_df[reference_df[identifier_column]==identifier]
		evaluation_path = identifier_df["Evaluation_path"].values[0]
		identifier_data = {}
		for metadata_column in metadata_columns:
			identifier_data[metadata_columns[metadata_column]] = identifier_df[metadata_column].values[0]
		for period in periods:
			period_start, period_end = periods[period]
			sums = processing.timedelta_sums(evaluation_path, index_name=identifier, period_start=period_start, period_end=period_end)
			#We need to calculate this explicitly since the start/end of th experiment may not align perfecty with the theoretical period
			real_period_duration = sums.sum(axis=1).values[0]
			#if the behaviour key is not found, there was none of that behaviour type in the period
			try:
				behaviour_ratio = sums[behaviour].values[0]/real_period_duration
			except KeyError:
				behaviour_ratio = 0
			identifier_data[behaviour+" ratio"] = behaviour_ratio
			identifier_data[period_label] = period
			identifier_data["identifier"] = identifier
			period_df_slice = pd.DataFrame(identifier_data, index=[identifier])
			evaluation_df = pd.concat([evaluation_df, period_df_slice])

	#data is usually ordered as it comes, for nicer plots we sort it here
	evaluation_df = evaluation_df.sort_values([period_label], ascending=True)
	evaluation_df = evaluation_df.sort_values(list(metadata_columns.values()), ascending=False)
	return evaluation_df

def plottable_sucrosepreference_df(reference_df):
	cage_ids = list(set(reference_df["Cage_id"]))
	preferences_df = pd.DataFrame({})
	for cage_id in cage_ids:
		cage_id_df = reference_df[reference_df["Cage_id"]==cage_id]
		reference_dates = list(set(cage_id_df["SucrosePreferenceMeasurement_reference_date"]))
		reference_dates.sort()
		measurement_dates = list(set(cage_id_df["SucrosePreferenceMeasurement_date"]))
		measurement_dates.sort()
		first_date = reference_dates[0]
		preferences={}
		for measurement_date in measurement_dates:
			cage_id_measurement_df = cage_id_df[cage_id_df["SucrosePreferenceMeasurement_date"] == measurement_date]
			start_date = cage_id_measurement_df["SucrosePreferenceMeasurement_reference_date"].tolist()[0]
			relative_start_day = start_date-first_date
			rounded_relative_start_day = processing.rounded_days(relative_start_day)
			relative_end_day = measurement_date-first_date
			rounded_relative_end_day = processing.rounded_days(relative_end_day)
			key = "{} to {}".format(rounded_relative_start_day, rounded_relative_end_day)
			water_start = cage_id_measurement_df["SucrosePreferenceMeasurement_water_start_amount"].tolist()[0]
			water_end = cage_id_measurement_df["SucrosePreferenceMeasurement_water_end_amount"].tolist()[0]
			sucrose_start = cage_id_measurement_df["SucrosePreferenceMeasurement_sucrose_start_amount"].tolist()[0]
			sucrose_end = cage_id_measurement_df["SucrosePreferenceMeasurement_sucrose_end_amount"].tolist()[0]
			water_consumption = water_end - water_start
			sucrose_consumption = sucrose_end - sucrose_start
			sucrose_prefernce = sucrose_consumption/(water_consumption + sucrose_consumption)
			preferences["Period [days]"] = key
			preferences["Sucrose Preference Ratio"] = sucrose_prefernce
			preferences["treatment"] = cage_id_measurement_df["TreatmentProtocol_code"].tolist()[0]
			preferences["cage id"] = cage_id # this may not actually be needed, as the same info is contained in the index
			preferences_df_slice = pd.DataFrame(preferences, index=[cage_id])
			preferences_df = pd.concat([preferences_df, preferences_df_slice])

	return preferences_df
