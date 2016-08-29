from __future__ import division
import numpy as np
import pandas as pd


def organize_demographydata( in_df, var_list, demography_list ):
	'''
	This is usefull for 1970's, 1980, and 1981-1989 dataframes. It
	puts data with year and state in columns, with population by age and 
	race in rows.
	'''
	out_df = in_df[ in_df.race_sex=='white_male']
	names = {a:a+'_white_male' for a in var_list}
	out_df.rename(columns = names, inplace = True)

	for demography in demography_list[1:]:
		df = in_df[ in_df.race_sex==demography]	
		df.drop('race_sex', axis=1, inplace=True)		
		names = {a:a+'_'+demography for a in var_list}
		df.rename(columns=names, inplace=True)
		out_df = out_df.merge(df, left_on=['year','fips'], right_on=['year','fips'], copy=False)	

	out_df['total'] = out_df[['total_'+j for j in demography_list]].sum(axis=1)
	out_df.drop('race_sex', axis=1, inplace=True)

	return out_df


def add_totals(df, demography_list):
	'''
	Given a dataframe with age and race as columns, find the
	population total by race each year (row).
	'''
	for d in demography_list:
		df['total_'+d] = df[[a+'_'+d for a in age_list]].sum(axis=1)

	df['total'] = df.filter(like='total',axis=1).sum(axis=1)
	return df	


if __name__ == '__main__':
	#-----------------------------
	# initial list of variables
	#-----------------------------
	age_list = ['0-4','5-9','10-14','15-19','20-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79','80-84','85+']
	var_list = age_list + ['total']
	demography_list = ['white_male','white_female','black_male','black_female','other_male','other_female']

	#---------1970s data----------
	# pull in demographic data
	#-----------------------------
	age_df_temp = pd.read_excel("../data/agedist_by_state.xlsx", sheetname='1970s')
	age_df_temp.drop('state', axis=1, inplace=True)

	# put data in desired shape (year,state in columns, population by age and race in rows)
	age_df = organize_demographydata( age_df_temp, var_list, demography_list  )

	#---------1980 data-----------
	# pull in demographic data
	#-----------------------------
	age_df_1980 = pd.read_excel("../data/agedist_by_state.xlsx", sheetname='1980')

	# this is county-level data, group at the state level, fix 'year','fips', and 'race_sex' variables
	age_df_1980['state_fips'] = age_df_1980.fips.astype('str').str.zfill(5).str[:2].astype(int)
	age_df_temp2 = age_df_1980.groupby(['state_fips','race_sex']).agg(np.sum)
	age_df_temp2['year'] = 1980
	age_df_temp2['fips'] = [j[0] for j in age_df_temp2.index]
	age_df_temp2['race_sex'] = [j[1] for j in age_df_temp2.index]
	age_df_temp2.index = range(len(age_df_temp2))

	age_df2 = organize_demographydata( age_df_temp2, var_list, demography_list )


	#---------1981-1989 data-----------
	# pull in demographic data
	#----------------------------------
	age_df_1981 = pd.read_excel("../data/agedist_by_state.xlsx", sheetname='1980s')
	age_df_1981['info'] = age_df_1981['info'].astype('str').str.zfill(5)

	age_df_1981['fips'] = age_df_1981['info'].str[0:2].astype(int)
	age_df_1981['year'] = 1980 + age_df_1981['info'].str[2].astype(int)
	age_df_1981['race_sex'] = age_df_1981['info'].str[3:5].astype(int)

	age_df_1981['race_sex'].replace(to_replace={11:'white_male',
												12:'white_female',
												51:'white_male',
												52:'white_female',
												21:'black_male',
												22:'black_female',
												61:'black_male',
												62:'black_female',
												31:'other_male',
												32:'other_female',
												71:'other_male',
												72:'other_female',
												41:'other_male',
												42:'other_female',
												81:'other_male',
												82:'other_female'}, inplace=True)


	# data has some extra race variables compared to 1970-1980, group by basic race variables to be consistent
	age_df_temp3 = age_df_1981.groupby(['fips','year','race_sex']).agg(np.sum)
	age_df_temp3['fips'] = [j[0] for j in age_df_temp3.index]
	age_df_temp3['year'] = [j[1] for j in age_df_temp3.index]
	age_df_temp3['race_sex'] = [j[2] for j in age_df_temp3.index]
	age_df_temp3.index = range(len(age_df_temp3))

	# reshape to desired format
	age_df3 = organize_demographydata( age_df_temp3, var_list, demography_list )

	#--------- 1990-1999 data ----------
	# pull in demographic data
	#-----------------------------------
	age_df_1990 = pd.read_excel("../data/agedist_by_state.xlsx", sheetname='1990s')
	age_df_1990['age_bucket'] = 0
	for i in range(len(age_list)):
		age_df_1990.loc[age_df_1990['age'] >5*i+4, 'age_bucket'] +=1

	# group over extra race variables (rows)
	age_df_temp4 = age_df_1990.groupby(['fips','year','age_bucket']).agg(np.sum)
	age_df_temp4['fips'] = [j[0] for j in age_df_temp4.index]
	age_df_temp4['year'] = [j[1] for j in age_df_temp4.index]
	age_df_temp4['age_bucket'] = [j[2] for j in age_df_temp4.index]
	age_df_temp4.index = range(len(age_df_temp4))

	# group over ethnicity variables (columns)
	age_df_temp4['white_male'] = age_df_temp4[['non-hispanic-white-male','hispanic-white-male']].sum(axis=1)
	age_df_temp4['white_female'] = age_df_temp4[['non-hispanic-white-female','hispanic-white-female']].sum(axis=1)
	age_df_temp4['black_male'] = age_df_temp4[['non-hispanic-black-male','hispanic-black-male']].sum(axis=1)
	age_df_temp4['black_female'] = age_df_temp4[['non-hispanic-black-female','hispanic-black-female']].sum(axis=1)
	age_df_temp4['other_male'] = age_df_temp4[['non-hispanic-aian-male','non-hispanic-api-male','hispanic-aian-male','hispanic-api-male']].sum(axis=1)
	age_df_temp4['other_female'] = age_df_temp4[['non-hispanic-aian-female','non-hispanic-api-female','hispanic-aian-female','hispanic-api-female']].sum(axis=1)

	# drop old ethnicity variables
	cols = [c for c in age_df_temp4.columns if 'hispanic' not in c]
	age_df_temp4 = age_df_temp4[cols]

	# rename variables to 1970,1980,1981 conventions
	# get population variables (skip "year" and "fips")
	cols = [c for c in age_df_temp4.columns if 'male' in c]

	# make a new dataframe, iteratively merge each age group (from rows) as new columns
	a = age_list[0]
	age_df4 = age_df_temp4[ age_df_temp4.age_bucket==0]
	names = {c: a+'_'+c for c in cols}
	age_df4.rename(columns=names, inplace=True)
	age_df4.drop(['age_bucket','age'], axis=1, inplace=True)		

	for ia, a in enumerate(age_list[1:]):
		df = age_df_temp4[ age_df_temp4.age_bucket==ia+1]
		names = {c: a+'_'+c for c in cols}	
		df.rename(columns=names, inplace=True)
		df.drop(['age_bucket','age'], axis=1, inplace=True)		
		age_df4 = age_df4.merge(df, left_on=['year','fips'], right_on=['year','fips'], copy=False)	

	# add totals for demographic variables
	age_df4 = add_totals(age_df4, demography_list)

	#--------- 2000-2010 data ----------
	# pull in demographic data
	#-----------------------------------
	age_df_2000 = pd.read_excel("../data/agedist_by_state.xlsx", sheetname='2000s')

	# drop extra data
	age_df_2000 = age_df_2000[age_df_2000.fips>0]
	age_df_2000 = age_df_2000[age_df_2000.age_bucket>0]
	age_df_2000 = age_df_2000[age_df_2000.sex>0]
	age_df_2000 = age_df_2000[age_df_2000.RACE>0]
	age_df_2000.RACE = np.minimum(3, age_df_2000.RACE)
	age_df_2000 = age_df_2000[age_df_2000.ORIGIN==0]
	age_df_2000.drop('ORIGIN', axis=1, inplace=True)

	# group over extra race variables
	age_df_temp5 = age_df_2000.groupby(['fips','states','RACE','sex','age_bucket']).agg(np.sum)
	age_df_temp5['fips'] = [ j[0] for j in age_df_temp5.index ]
	age_df_temp5['states'] = [ j[1] for j in age_df_temp5.index ]	
	age_df_temp5['RACE'] = [ j[2] for j in age_df_temp5.index ]	
	age_df_temp5['sex'] = [ j[3] for j in age_df_temp5.index ]	
	age_df_temp5['age_bucket'] = [ j[4] for j in age_df_temp5.index ]	
	age_df_temp5.index = range(len(age_df_temp5))

	# put year columns into rows and race/age rows into columns
	age_df5 = pd.DataFrame()
	for fip in age_df3.fips.unique():
		temp_df5 = pd.DataFrame()
		temp_df5['year'] = range(2000,2011)
		temp_df5['fips'] = fip

		for sx, sxname in enumerate(['_male','_female']):
			for r, rname in enumerate(['_white','_black','_other']):
				df = age_df_temp5.filter(like='POPESTIMATE')[(age_df_temp5.fips==fip) & (age_df_temp5.sex==sx+1) & (age_df_temp5.RACE==r+1)].T
				df.columns = [a+rname+sxname for a in age_list]
				df['year'] = range(2000,2011)
				
				temp_df5 = temp_df5.merge(df, left_on='year',right_on='year')

		age_df5 = pd.concat([age_df5,temp_df5])

	# add totals over demographic variables
	age_df5 = add_totals(age_df5, demography_list)


	#--------- 2011-2014 data ----------
	# pull in demographic data
	#-----------------------------------
	age_df_2010 = pd.read_excel("../data/agedist_by_state.xlsx", sheetname='2010s')

	# mostly in the right shape, just drop some extra variables
	age_df_2010 = age_df_2010[ (age_df_2010.hispanic=='totpop') & (age_df_2010.year!='est42010') & (age_df_2010.year!='cen42010') ]
	age_df_2010['year'] = age_df_2010.year.str[4:].astype(int)
	age_df_2010.drop('hispanic', axis=1, inplace=True)
	age_df_2010 = age_df_2010[age_df_2010['year']>2010]
	age_df_2010 = age_df_2010[[c for c in age_df_2010.columns if 'Total' not in c]]

	# raname columns, combine extra race columns into "other"
	columns = age_df_2010.columns[2:]
	for a in age_list:
		for s in ['male','female']:
			name = a + '_other_' +s
			cols = [c for c in columns if a==c.split(';')[2].strip() and s== c.split(';')[1].strip() ]
			cols = [c for c in cols if 'asian' in c or 'Two or More Races' in c or 'napi' in c or 'aian' in c ]		
			age_df_2010[name] = age_df_2010[cols].sum(axis=1)
			age_df_2010.drop(cols,axis=1,inplace=True)

	# rename remaining columns
	rename_dict={}
	for c in age_df_2010.columns:
		if ';' in c:
			parts = c.split(';')
			name = parts[2].strip()+'_'+parts[0].strip()+'_'+parts[1].strip()
			rename_dict[c] = name		

	age_df_2010.rename(columns=rename_dict, inplace=True)

	#-----------------------------------
	# add totals over demographic groups
	#-----------------------------------
	age_df6 = add_totals(age_df_2010, demography_list)

	#-----------------------------------
	# combine all demographic dataframes
	#-----------------------------------
	age_df = age_df.append([age_df2, age_df3, age_df4, age_df5, age_df6], ignore_index=True)
	
	#-----------------------------------
	# add name of states
	#-----------------------------------
	age_df.merge( age_df_temp5[['fips','states']], left_on='fips', right_on='fips')

	#-----------------------------------
	# save data
	#-----------------------------------
	age_df.to_pickle('../results/age_race_df.p')
	age_df.to_stata('../results/age_race_df.dta')
