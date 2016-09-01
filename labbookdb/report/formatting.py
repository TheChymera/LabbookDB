import pandas as pd
import processing

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
