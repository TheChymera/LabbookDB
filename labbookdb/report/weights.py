__author__="Horea Christian"
import sys
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
from os import path
from sqlalchemy import create_engine, or_, inspection
from sqlalchemy.orm import sessionmaker, aliased

sys.path.append('/home/chymera/src/LabbookDB/db/')
from common_classes import *
from query import loadSession, allowed_classes

import matplotlib
matplotlib.style.use('ggplot')

def weights_plot(db_path, animals={}, start_date=None, end_date=None, include_relationship_columns=[], normalize=True):
	include_relationship_columns.append("weights")
	session, engine = loadSession(db_path)

	cols = []
	joins = []
	insp = inspection.inspect(Animal)
	for name, col in insp.columns.items():
		cols.append(col.label(name))
	for name, rel in insp.relationships.items():
		if name not in include_relationship_columns:
			continue
		alias = aliased(rel.mapper.class_, name=name)
		joins.append((alias, rel.class_attribute))
		for col_name, col in inspection.inspect(rel.mapper).columns.items():
			#the id column causes double entries, as it is mapped once on the parent table (related_table_id) and once on the child table (table_id)
			if col.key != "id":
				aliased_col = getattr(alias, col.key)
				cols.append(aliased_col.label("{}_{}".format(name, col_name)))

		sub_insp = inspection.inspect(rel.mapper.class_)
		for sub_name, sub_rel in sub_insp.relationships.items():
			if "contains" not in sub_name:
				sub_alias = aliased(sub_rel.mapper.class_, name=name+"_"+sub_name)
				joins.append((sub_alias, sub_rel.class_attribute))
				for sub_col_name, sub_col in inspection.inspect(sub_rel.mapper).columns.items():
					#the id column causes double entries, as it is mapped once on the parent table (related_table_id) and once on the child table (table_id)
					if sub_col.key != "id":
						sub_aliased_col = getattr(sub_alias, sub_col.key)
						cols.append(sub_aliased_col.label("{}_{}_{}".format(name, sub_name, sub_col_name)))

	sql_query = session.query(*cols).select_from(Animal)
	for join in joins:
		sql_query = sql_query.outerjoin(*join)

	sql_query = sql_query.filter(or_(Animal.birth_date == datetime.datetime(*[int(a) for a in birthdate.split(",")]) for birthdate in animals["birth_date"]))

	mystring = sql_query.statement
	df = pd.read_sql_query(mystring,engine)
	if normalize:
		reference_date = list(set(df[(df["treatments_protocol_code"] == "cFluDW")]["treatments_start_date"]))
		if len(reference_date) >= 2:
			raise IndexError("There are multiple start dates for the target treatment. Cannot normalize")
		reference_date = reference_date[0].date()
	for i in set(df["id"]):
		select = df[(df["id"]==i)]
		if "cFluDW" in set(select["treatments_protocol_code"]):
			if normalize:
				try:
					reference_value = select[(select["weights_date"].apply(pd.datetools.normalize_date) == reference_date)]["weights_weight"].tolist()[0]
				except IndexError:
					continue
				plt.plot(select["weights_date"],select["weights_weight"]/reference_value,"darkmagenta")
			else:
				plt.plot(select["weights_date"],select["weights_weight"],"darkmagenta")
		else:
			if normalize:
				try:
					reference_value = select[(select["weights_date"].apply(pd.datetools.normalize_date) == reference_date)]["weights_weight"].tolist()[0]
				except IndexError:
					continue
				plt.plot(select["weights_date"],select["weights_weight"]/reference_value,"limegreen")
			else:
				plt.plot(select["weights_date"],select["weights_weight"], "limegreen")

		line1 = matplotlib.lines.Line2D([], [], color='darkmagenta', markersize=15, label='cFluDw')
		line2 = matplotlib.lines.Line2D([], [], color='limegreen', markersize=15, label='control')
		plt.legend(handles=[line1, line2],bbox_to_anchor=(1,1))

if __name__ == '__main__':
	weights_plot("~/syncdata/meta.db", {"birth_date":["2016,1,12"]}, include_relationship_columns=["treatments", "measurements"], normalize=True)
	# weights_plot("~/syncdata/meta.db", [36,39,40,26,28,29,30], include_relationship_columns=["treatments", "measurements"])
	# weights_plot("~/syncdata/meta.db", [1,5,7,8,9,11,12], include_relationship_columns=["treatments", "measurements"])
	plt.show()
