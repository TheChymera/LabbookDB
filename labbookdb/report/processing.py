def rounded_days(datetime_obj):
	days = datetime_obj.days
	# rounding number of days up, as timedelta.days returns the floor only:
	if datetime_obj.seconds / 43199.5 >= 1:
		days += 1
	return days
