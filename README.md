#Merging census Historical Data (Age, Sex, Race)

This mini-project takes an assortment of census spreadsheets and combines them into a single pandas DataFrame (also a Stata .dta file). The variables include age (5 year bins), sex, and race (white/black/other), from 1970 to 2014. The census spreadsheets differ significantly from decade to decade, so the bulk of work is making the data consistent across time. 

Other variables include fips (census id for state), year, and name of state. The data are organized with year and state in columns. Each subset of the population is in its own column (e.g. '10-14_black_female' means black females ages 10 to 14). Subtotals by race and gender are also included. 

Link to [Census data](https://www.census.gov/popest/data/historical/index.html). 


+   Author: Benjamin Tengelsen
+   Date: Aug 9, 2016
+   Code: Python 2.7, pandas, numpy