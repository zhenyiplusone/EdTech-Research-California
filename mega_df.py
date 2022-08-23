'''
Combines all the e-rate data into one big spreadsheet along with creating identifiers
'''
import pandas as pd 
import numpy as np
import os
import csv
from xlsxwriter.workbook import Workbook

# Add some command-line logic to read the file names.
def convert():
	for year in range(2012, 2016):
		tsv_file = f"E-Rate_Funding/District/{year}_District_Funding.tsv"
		xlsx_file = f"E-Rate_Funding/District/{year}_District_Funding.xlsx"

		# Create an XlsxWriter workbook object and add a worksheet.
		workbook = Workbook(xlsx_file)
		worksheet = workbook.add_worksheet()

		# Create a TSV file reader.
		tsv_reader = csv.reader(open(tsv_file,'rt'),delimiter="\t")

		# Read the row data from the TSV file and write it to the XLSX file.
		for row, data in enumerate(tsv_reader):
		    worksheet.write_row(row, 0, data)

		# Close the XLSX file.
		workbook.close()

def create_mega(type_data):
	mega_df = pd.DataFrame()

	for year in range(2015,2020):
		df_to_add = pd.read_excel(f"E-Rate_Funding/{type_data}/{year}_{type_data}_Funding.xlsx")
		mega_df = mega_df.append(df_to_add)
	
	mega_df['First_Iden'] = mega_df['Applicant Name'].apply(lambda x: x.split(' ')[0])
	mega_df['Second_Iden'] = mega_df['Applicant Street Address1'].apply(lambda x: x.split(' ')[0])
	mega_df[f'{type_data.upper()}ADDRESSIDENTIFIER'] = mega_df['First_Iden'] + "_" + mega_df['Applicant Zip Code'].astype(str) + "_" + mega_df['Second_Iden']
	'''mega_df = mega_df[[f'{type_data.upper()}ADDRESSIDENTIFIER','Funding Year','Committed Amount','Cmtd Total Cost','Total Authorized Disbursement',]]
	
	agg_df = mega_df.groupby([f'{type_data.upper()}ADDRESSIDENTIFIER',"Funding Year"]).sum()
	agg_df[f'{type_data.upper()}ADDRESSIDENTIFIER Year'] = agg_df.index.get_level_values(0)'''

	#Mega_df 2.0
	mega_df = mega_df[['Applicant Name',f'{type_data.upper()}ADDRESSIDENTIFIER', 'Funding Year','Committed Amount','Cmtd Total Cost','Total Authorized Disbursement',]]
	agg_df = mega_df.groupby([f'{type_data.upper()}ADDRESSIDENTIFIER',"Funding Year"]).sum()
	agg_df[f'{type_data.upper()}ADDRESSIDENTIFIER'] = agg_df.index.get_level_values(0)

	#Make the column name lower case for Cali data set
	#Rename for Cali dataset

	agg_df['Funding Year'] = agg_df.index.get_level_values(1)
	agg_df['Applicant Name'] = agg_df[f'{type_data.upper()}ADDRESSIDENTIFIER'].apply(lambda x: mega_df[mega_df[f'{type_data.upper()}ADDRESSIDENTIFIER'] == x].iloc[0]['Applicant Name'])

	agg_df.rename(columns = {'Funding Year': 'testyear'}, inplace=True)
	agg_df[f'{type_data.upper()}ADDRESSIDENTIFIER'] = agg_df[f'{type_data.upper()}ADDRESSIDENTIFIER'].str.lower()
	agg_df.to_excel(f"E-Rate_Funding/{type_data}_Mega_Sheet_2.xlsx", index = False)

create_mega("District")
