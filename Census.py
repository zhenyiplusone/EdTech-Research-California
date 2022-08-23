'''
Gets data from Census gov API for median household income and population
'''
import requests
import json
import pandas as pd
import numpy as np
import urllib

count = pd.read_csv('EarnedIncome/EarnedIncomeCA1819.csv') # can also index sheet by name or fetch all sheets
county_list = count['county'].tolist()

def download_data():
	'''
	Downloads spreadsheet containing median household income
	'''
	for year in range(2000, 2019):
		dls = f"https://www2.census.gov/programs-surveys/saipe/datasets/{year}/{year}-state-and-county/est{str(year)[2:]}all.xls"
		urllib.request.urlretrieve(dls, f"est{str(year)[2:]}all.xls")
	#Remember to run this first and then move it to the EST folders

#download_data()

def read_data():
	'''
	Reads the Census data for median household income
	'''
	combined_df = pd.DataFrame(columns = ['Year', 'County FIPS Code', 'Median Household Income'])
	for year in range(2000, 2019):
		df = pd.read_excel(f'EST/est{str(year)[2:]}all.xls', skiprows=2)
		df = df.loc[((df['State FIPS Code'] == 6) | (df['State FIPS Code'] == "06")) & (df['County FIPS Code'] != 0)][['County FIPS Code', 'Median Household Income']]
		df['Year'] = year
		combined_df = combined_df.append(df,ignore_index=True)
	fiscal_df = pd.DataFrame(columns = ['FY', 'CountyID', 'Median Household Income'])
	for county in county_list:
		for year in range(2000, 2019):
			median_income = combined_df.loc[(combined_df['County FIPS Code'] == county) & ((combined_df['Year'] == year) | (combined_df['Year'] == year+1))]['Median Household Income'].mean()
			df_add = {'CountyID': county, 'FY': year+1, 'Median Household Income': median_income}
			fiscal_df = fiscal_df.append(df_add, ignore_index=True)
	return fiscal_df

def population():
	'''
	Uses population data from cancer center.txt and creates dataframe
	'''
	raw_df = pd.read_csv('ca.1969_2020.19ages.txt')
	print(raw_df)
	cleaned_df = pd.DataFrame(columns = ["Year", "CountyID", "Population"])
	cleaned_df["Year"] = raw_df['Text'].astype(str).str[0:4].astype(int)
	cleaned_df["CountyID"] = raw_df['Text'].astype(str).str[8:11].astype(int)
	cleaned_df["Population"] = raw_df['Text'].astype(str).str[18:].astype(int)
	cleaned_df = cleaned_df.groupby(["Year", "CountyID"], as_index=False)['Population'].sum()
	cleaned_df = cleaned_df.loc[cleaned_df["Year"] >= 2000]
	pop_df = pd.DataFrame(columns = ['FY', 'CountyID', 'Population'])
	for county in county_list:
		for year in range(2000, 2019):
			population = cleaned_df.loc[(cleaned_df['CountyID'] == county) & ((cleaned_df['Year'] == year) | (cleaned_df['Year'] == year+1))]['Population'].mean()
			df_add = {'CountyID': county, 'FY': year+1, 'Population': population}
			pop_df = pop_df.append(df_add, ignore_index=True)
	print(pop_df)
	return pop_df
	#print(cleaned_df.loc[(cleaned_df["Year"] == 2019)].sum())

def combine_med_income_unemploy(med_df, pop_df):
	'''
	Combines median household income and population dataframe with the one regarding unemployment
	'''
	fiscal_df = pd.read_excel('CACountyUnemploymentRateFiscalYears.xlsx')
	fiscal_df['Median Household Income'] = med_df['Median Household Income']
	fiscal_df['Population'] = pop_df["Population"]
	wifi_df = pd.read_excel("CACountyWifi.xlsx")
	fiscal_df = fiscal_df.merge(wifi_df, how='left', on=["FY", "CountyID"])
	fiscal_df.to_excel("CACountyEcon.xlsx",index=False)

med_df = read_data()
pop_df = population()
combine_med_income_unemploy(med_df, pop_df)