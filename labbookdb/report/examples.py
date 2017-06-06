import matplotlib.pyplot as plt
from behaviopy import plotting
try:
	from .behaviour import forced_swim, sucrose_preference
	from .protocolize import compose_tex, print_document
	from .tracking import treatments_plot
	from .selection import animals_by_treatment
except SystemError:
	from labbookdb.report.behaviour import forced_swim, sucrose_preference
	from labbookdb.report.protocolize import compose_tex, print_document
	from labbookdb.report.tracking import treatments_plot
	from labbookdb.report.selection import animals_by_treatment

COHORTS = [
	{"treatment_start":"2015,11,11", "window_end":"2015,12,30"},
	{"treatment_start":"2016,4,25,19,30", "window_end":""},
	{"treatment_start":"2016,5,19,23,5", "window_end":""},
	{"treatment_start":"2016,11,24,21,30", "window_end":""},
	{"treatment_start":"2017,1,31,22,0", "window_end":"2017,3,21"},
	]

def my_sucrose_preference(db_path, cohorts, compare):
	if cohorts == "cage":
		treatment_start_dates = ["2016,4,25,19,30","2016,5,19,23,5",]
	elif cohorts == "animal":
		treatment_start_dates = ["2016,11,24,21,30"]
	elif cohorts == "aileen_switching_sides":
		treatment_start_dates = ["2017,1,31,22,0"]
	elif cohorts == "all":
		treatment_start_dates = [i["treatment_start"] for i in COHORTS]
	else:
		treatment_start_dates = cohorts
	if compare == "treatment":
		sucrose_preference(db_path, treatment_start_dates=treatment_start_dates, comparisons={"Period [days]":[]}, compare="Treatment",save_df="")
	elif compare == "side_preference":
		sucrose_preference(db_path, treatment_start_dates=treatment_start_dates, comparisons={"Cage ID":[]}, compare="Sucrose Bottle Position", save_df="")

def treatments(db_path, cohorts,
	per_cage=True,
	):

	if isinstance(cohorts,str):
		cohorts = [cohorts]
	shade = ["FMRIMeasurement_date"]
	draw = [
		{"TreatmentProtocol_code":["aFluIV_","Treatment_start_date"]},
		{"TreatmentProtocol_code":["aFluIV","Treatment_start_date"]},
		"OpenFieldTestMeasurement_date",
		"ForcedSwimTestMeasurement_date",
		{"TreatmentProtocol_code":["aFluSC","Treatment_start_date"]},
		]
	saturate = [
		{"Cage_TreatmentProtocol_code":["cFluDW","Cage_Treatment_start_date","Cage_Treatment_end_date"]},
		{"Cage_TreatmentProtocol_code":["cFluDW_","Cage_Treatment_start_date","Cage_Treatment_end_date"]},
		{"TreatmentProtocol_code":["cFluIP","Treatment_start_date","Treatment_end_date"]},
		]
	if per_cage:
		filters = [["Cage_Treatment","start_date",i["treatment_start"]] for i in cohorts]
	else:
		df = animals_by_treatment(db_path, start_dates=[i["treatment_start"] for i in cohorts],)
		animals = list(set(df["Animal_id"]))
		animals = [str(i) for i in animals]
		myfilter = ["Animal","id",]
		myfilter.extend(animals)
		filters = [myfilter]
	window_end = [i["window_end"] for i in cohorts if i["window_end"] not in ("", None)]
	window_end.sort()
	if window_end:
		window_end = window_end[-1]
	treatments_plot(db_path,
		draw=draw,
		filters=filters,
		saturate=saturate,
		default_join="outer",
		#This loads only entries with fMRI measurements:
		# join_types=["outer","inner","outer","outer","outer","outer","outer","outer","outer","outer"],
		#This loads all entries:
		join_types=["outer","outer","outer","outer","outer","outer","outer","outer","outer","outer"],
		save_df="~/lala.csv",
		save_plot="~/lala.png",
		shade=shade,
		window_end=window_end,
		)

def protocol(db_path,
	class_name="DNAExtractionProtocol",
	code="EPDqEP",
	):
	tex = compose_tex(db_path, class_name,code)
	print_document(tex, class_name+"_"+code+".pdf")

if __name__ == '__main__':
	db_path="~/syncdata/meta.db"
	# treatments(db_path,COHORTS[0:1], per_cage=False)
	# treatments(db_path,COHORTS[2:3])
	# forced_swim(db_path, "tsplot", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5"])

	################################################
	#####Safe for usage with logging_examples#######
	################################################
	# treatments(db_path,COHORTS[4:5])
	# my_sucrose_preference(db_path, "aileen_switching_sides", "treatment")
	forced_swim(db_path, "tsplot", treatment_start_dates=["2017,1,31,22,0","2016,11,24,21,30"])
	# forced_swim(db_path, "tsplot", treatment_start_dates=["2017,1,31,22,0"])
	# forced_swim(db_path, "pointplot", treatment_start_dates=["2017,1,31,22,0"])
	# forced_swim(db_path, "tsplot", treatment_start_dates=["2016,11,24,21,30"])
	# forced_swim(db_path, "tsplot", treatment_start_dates=[i["treatment_start"] for i in COHORTS], save_df="")
	# forced_swim(db_path, "pointplot", treatment_start_dates=[i["treatment_start"] for i in COHORTS], save_df="")
	# forced_swim(db_path, "ttest", treatment_start_dates=["2016,11,24,21,30","2017,1,31,22,0"], columns=["2 to 4", "2 to 6"])
	# forced_swim(db_path, "ttest", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5","2017,1,31,22,0"], columns=["2 to 4", "2 to 6"])
	# forced_swim(db_path, "ttest", treatment_start_dates=["2016,4,25,19,30","2016,5,19,23,5","2016,11,24,21,30","2017,1,31,22,0"], columns=["2 to 4", "2 to 6"], colorset=["#56B4E9", "#E69F00", "#56B4E9", "#000000","#F0E442", "#0072B2", "#D55E00", "#CC79A7"])
	# forced_swim(db_path, "ttest", treatment_start_dates=["2017,1,31,22,0"], columns=["2 to 4"])
	# forced_swim(db_path, "ttest", treatment_start_dates=["2016,11,24,21,30"], columns=["2 to 4", "2 to 6"])
	# forced_swim(db_path, "ttest", treatment_start_dates=[i["treatment_start"] for i in COHORTS], columns=["2 to 4", "2 to 6"], save_df="")
	# protocolize_dna_extraction(db_path)

	# plt.savefig("fst.pdf")
	plt.show()
