import datetime

def arange_by_date(attribute):
	strs = [attribute[i].__str__() for i in range(len(attribute))]
	try:
		dates = [dt_format(attribute[i].date) for i in range(len(attribute))]
	except:
		dates = [dt_format(attribute[i].start_date) for i in range(len(attribute))]
	strs = [m for _,m in sorted(zip(dates,strs))]
	return strs

def dt_format(dt):
	if not dt:
		return "NO DATE"
	elif dt.time()==datetime.time(0,0,0):
		return str(dt.date())
	else:
		return str(dt)

