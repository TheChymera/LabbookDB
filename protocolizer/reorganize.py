import os
import pandas as pd
import numpy as np


def remix_csv_christian(source_directory, extension=None, destination_directory=None):
	if not destination_directory:
		destination_directory = source_directory

	filters = {
	"age columns":['lane','ID','volume [\xc2\xb5l]','ladder','agarose in gel [%]','comment'],
	"pcr columns":['ID','pcr mix','DNA sample','primers','PCR annealing [\xc2\xb0C]','comment']
	}

	source_files = os.listdir(source_directory)
	# only select files matching the extension, the boolean check ensures files with no extension are dropped
	source_files = [source_file for source_file in source_files if os.path.splitext(source_file)[-1] and os.path.splitext(source_file)[-1] in extension]

	columns=[]
	for source_file in source_files:
		file_df = pd.read_csv(source_directory+"/"+source_file)

		#selecting workaround if some ID-generating columsn are absent
		workaround=0
		if not 'volume [\xc2\xb5l]' in file_df.columns:
			workaround += 1

		age_df = file_df.filter(items=filters["age columns"])
		pcr_df = file_df.filter(items=filters["pcr columns"])

		#prepare missing columns
		for column_name in filters["age columns"]:
			if not column_name in age_df.columns:
				age_df[column_name]=np.nan
		for column_name in filters["pcr columns"]:
			if not column_name in pcr_df.columns:
				pcr_df[column_name]=np.nan

		#create ID list
		source_file_base = os.path.splitext(source_file)[0]
		if workaround == 1:
			new_ID_count = len(age_df.loc[((pcr_df['primers'].notnull()) | (pcr_df['pcr mix'].notnull())) & (age_df['ID'].isnull()) & (age_df['ladder'].isnull()),"ID"])
		else:
			new_ID_count = len(age_df.loc[(age_df['volume [\xc2\xb5l]'].notnull()) & (age_df['ID'].isnull()) & (age_df['ladder'].isnull()),"ID"])
		new_ID_list = [source_file_base+"_"+"%02d" % ordinal for ordinal in range(new_ID_count)]

		#assigning new IDs. CAREFUL!! the following 2 lines only work assuming that the dataframes have the same length
		if workaround == 1:
			pcr_df.loc[((pcr_df['primers'].notnull()) | (pcr_df['pcr mix'].notnull())) & (age_df['ID'].isnull()) & (age_df['ladder'].isnull()),"ID"] = new_ID_list
			age_df.loc[((pcr_df['primers'].notnull()) | (pcr_df['pcr mix'].notnull())) & (age_df['ID'].isnull()) & (age_df['ladder'].isnull()),"ID"] = new_ID_list
		else:
			pcr_df.loc[(age_df['volume [\xc2\xb5l]'].notnull()) & (age_df['ID'].isnull()) & (age_df['ladder'].isnull()),"ID"] = new_ID_list
			age_df.loc[(age_df['volume [\xc2\xb5l]'].notnull()) & (age_df['ID'].isnull()) & (age_df['ladder'].isnull()),"ID"] = new_ID_list

		#truncating
		pcr_df = pcr_df[pcr_df.ID.notnull()]

		#filling in values as needed
		if 'agarose in gel [%]' in file_df.columns:
			age_df.loc[age_df['agarose in gel [%]'].isnull(),'agarose in gel [%]'] = age_df[age_df['agarose in gel [%]'].notnull()]['agarose in gel [%]'].ix[1]

		#rename columns
		age_df.rename(columns={'ID':'DNA sample'}, inplace=True)

		#save files
		age_df.to_csv(source_directory.replace("gel_electrophoresis", "age")+'/'+source_file.replace("pcr", "age"), index=False)
		pcr_df.to_csv(source_directory.replace("gel_electrophoresis", "pcr")+'/'+source_file, index=False)

if __name__ == "__main__":
	source_directory="/home/chymera/data/gt.ep/gel_electrophoresis"
	remix_csv_christian(source_directory, extension=".csv")
