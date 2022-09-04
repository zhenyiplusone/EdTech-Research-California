import pandas as pd 

count = pd.read_csv('EarnedIncome/EarnedIncomeCA1819.csv') # can also index sheet by name or fetch all sheets
county_list = count['county'].tolist()

def convert_cata():
	mega_df = pd.DataFrame()
	for year in range(2011, 2016):
		df = pd.read_csv(f"Form477/county_connections_dec_{year}.csv", engine='python')
		if "countycode" in df.columns:
			df["state"] = df["countycode"].apply(lambda x: int(str(x)[:1]))
			df["county"] = df["countycode"].apply(lambda x: int(str(x)[1:]))
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].replace(1,100)
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].replace(2,300)
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].replace(3,500)
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].replace(4,700)
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].replace(5,900)
		df = df[df["state"] == 6]
		df['year'] = year
		df = df[['rfc_per_1000_hhs','state', 'county', 'year']]

		mega_df = mega_df.append(df, ignore_index=True)

	for year in range(2016, 2019):
		df = pd.read_csv(f"Form477/county_connections_dec_{year}.csv", engine='python')
		if "ï»¿countycode" in df.columns:
			df["state"] = df["ï»¿countycode"].apply(lambda x: int(str(x)[:1]))
			df["county"] = df["ï»¿countycode"].apply(lambda x: int(str(x)[1:]))
		df['ratio'] = df['ratio'].replace(-9999, None)
		df['rfc_per_1000_hhs'] = df['ratio']*1000
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].mask((df['rfc_per_1000_hhs'] > 0) & (df['rfc_per_1000_hhs'] <= 200), 100)
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].mask((df['rfc_per_1000_hhs'] > 200) & (df['rfc_per_1000_hhs'] <= 400), 300)
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].mask((df['rfc_per_1000_hhs'] > 400) & (df['rfc_per_1000_hhs'] <= 600), 500)
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].mask((df['rfc_per_1000_hhs'] > 600) & (df['rfc_per_1000_hhs'] <= 800), 700)
		df['rfc_per_1000_hhs'] = df['rfc_per_1000_hhs'].mask((df['rfc_per_1000_hhs'] > 800) & (df['rfc_per_1000_hhs'] <= 1000), 900)
		print(df)
		df = df[df["state"] == 6]
		df['year'] = year
		df = df[['rfc_per_1000_hhs','state', 'county', 'year']]
		mega_df = mega_df.append(df, ignore_index=True)

	fiscal_df = pd.DataFrame(columns = ['FY', 'CountyID', 'Wifi Connection Per 1000'])
	for county in county_list:
		for year in range(2011, 2018):
			wifi = mega_df.loc[(mega_df['county'] == county) & ((mega_df['year'] == year) | (mega_df['year'] == year+1))]['rfc_per_1000_hhs'].mean()
			df_add = {'CountyID': county, 'FY': year+1, 'Wifi Connection Per 1000': wifi}
			fiscal_df = fiscal_df.append(df_add, ignore_index=True)
	#fiscal_df[["CountyID", "FY", "Wifi Connection Per 1000"]] = fiscal_df[["CountyID", "FY", "Wifi Connection Per 1000"]].astype(int)
	return fiscal_df
fiscal_df = convert_cata()
fiscal_df.to_excel("CACountyWifi.xlsx",index=False)
