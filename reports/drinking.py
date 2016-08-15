__author__="Horea Christian"
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
from os import path
from sqlalchemy import create_engine, or_, inspection
from sqlalchemy.orm import sessionmaker, aliased, with_polymorphic, joinedload_all

sys.path.append('/home/chymera/src/LabbookDB/db/')
from common_classes import *
from query import loadSession, allowed_classes, get_df

import matplotlib
matplotlib.style.use('ggplot')

def sucrosepreference_plot(reference_df):
	cages = list(set(reference_df["Cage_id"]))
	print cages

if __name__ == '__main__':
	col_entries=[
		("Cage","id"),
		("Treatment",),
		("SucrosePreferenceMeasurement",),
		("TreatmentProtocol","code"),
		]
	join_entries=[
		("Cage.treatments",),
		("SucrosePreferenceMeasurement",),
		("Treatment.protocol",),
		]
	filters = [["Treatment","start_date","2016,4,25,19,30","2016,5,19,23,5"]]
	reference_df = get_df("~/syncdata/meta.db",col_entries=col_entries, join_entries=join_entries, filters=filters)

	sucrosepreference_plot(reference_df)
	# plt.show()
