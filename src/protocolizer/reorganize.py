import os
import pandas as pd

age_columns=[]

def remix_csv(source_directory, extension=None, destination_directory=None):
	if not destination_directory:
		destination_directory = source_directory

	source_files = os.listdir(source_directory)
	source_files = [source_file for source_file in source_files if os.path.splitext(source_file)[1] in extension]

	columns=[]
	for source_file in source_files:
		file_df = pd.read_csv(source_directory+"/"+source_file)
		columns += list(file_df.columns.values)
	print(set(columns))

if __name__ == "__main__":
	source_directory="/home/chymera/data/gt.ep/gel_electrophoresis"
	remix_csv(source_directory, ".csv")
