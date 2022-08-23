''' 
Gets the unemployment rate
'''
import requests
import json
import pandas as pd
import numpy as np

api_key = '7fd2cf6e8b14449dabe22fa42bb0e786'

count = pd.read_csv('EarnedIncome/EarnedIncomeCA1819.csv') # can also index sheet by name or fetch all sheets
county_list = count['county'].tolist()

def api_data():
    '''
    Converts data from API to raw excel sheet
    '''
    headers = {'Content-type': 'application/json'}
    ids = [f'LAUCN06{x:03d}0000000003' for x in county_list]

    final_df = pd.DataFrame(columns = ['year', 'period', 'value', 'countyid'])
    for id_break in range(int(len(ids)/20)+1):
        lower_bound = 20*id_break
        upper_bound = 20*(id_break+1)
        data = json.dumps({"seriesid": ids[lower_bound:upper_bound],"startyear":"2000", "endyear":"2019", "registrationkey": api_key})
        p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers).json()
        for series in p['Results']['series']:
            df = pd.DataFrame(series['data'])
            df = df.drop(columns=['periodName','footnotes'])
            df['countyid'] = series['seriesID'].split('LAUCN06')[1].split('0000000003')[0]
            final_df = final_df.append(df,ignore_index=True)

    final_df.to_excel("CACountyUnemploymentRateRaw.xlsx",index=False)

api_data()
#df_total = pd.wide_to_long(df_total, stubnames='ht', i=['year'], j='period')
def fiscal_year():
    '''
    Breaks the monthly data into ones that a school year and produces TXCountyUnemploymentRateFiscalYears.xlsx
    '''
    raw_df = pd.read_excel('CACountyUnemploymentRateRaw.xlsx')

    school_year_df = pd.DataFrame(columns = ['CountyID', 'FY', 'Unemployment Rate'])
    #print(np.where(raw_df['year'] == 2018, 'M07', 'M08','M09', 'M10','M11', 'M12'))

    first_sem = ['M07', 'M08','M09', 'M10','M11', 'M12']
    second_sem = ['M01', 'M02','M03', 'M04','M05', 'M06']
    print(raw_df.loc[(raw_df['countyid'] == 1) & (((raw_df['year'] == 2018) & (raw_df['period'].isin(first_sem))) | ((raw_df['year'] == 2019) & (raw_df['period'].isin(second_sem))))]['value'].mean())

    for county in county_list:
        for year in range(2000,2019):
            unemployment_rate = raw_df.loc[(raw_df['countyid'] == county) & (((raw_df['year'] == year) & (raw_df['period'].isin(first_sem))) | ((raw_df['year'] == year+1) & (raw_df['period'].isin(second_sem))))]['value'].mean()
            df_add = {'CountyID': county, 'FY': year+1, 'Unemployment Rate': unemployment_rate}
            school_year_df = school_year_df.append(df_add,ignore_index=True)

    print(school_year_df)
    school_year_df.to_excel("CACountyUnemploymentRateFiscalYears.xlsx",index=False)

fiscal_year()