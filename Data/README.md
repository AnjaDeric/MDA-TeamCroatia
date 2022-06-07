This folder contains all CSV files and data used and generated in the data collection, cleaning, and pre-processing steps of the project.

File Desctiptions
-----------------

**active_cases_1day**: contains basic information and _active_ case counts for all relevant counties for a single day (cleaned, no missing values)

**active_cases_2021**: contains basic information and _active_ case counts for all relevant counties for January 1st through December 31st of 2021 (cleaned, no missing values)

**active_cases_2021_scaled**: contains basic information and _active_ case counts for all relevant counties for January 1st through December 31st of 2021, scaled by population to units of 'per 100,000 people' (cleaned, no missing values)

**active_cases_2021_test**: contains basic information and _active_ case counts for all relevant counties for January 1st through December 31st of 2021, with the FIPS value for one South Dakota county adjusted to pre-2015 verion (cleaned, no missing values)

**adj_dist_all_final.csv**: contains a list of pairs of relevant counties that border each other as well as the great-circle distances, driving distances, and driving durations between them; this is the cleaned version of the adjacent_counties file and additioanlly only contains the relevant counties

**county_info**: contains a list of relevant US counties and basic info about them (FIPS, name, state, longitude, latitude, population)

**covid_symptom_test_data.csv**: contains data used for training a predictive model for COVID test result prediction

**all_predictions.csv**: contains all possible combinations of COVID symptoms and their respective predictions for the COVID prediction ML models

Notes
-----
* the term _relevant_ counties implies that all US territories as well as Alaska, Hawaii, and any island counties in the continental US have been filtered out from the data set
* most COVID data (including county_info and state_info) was collected and filtered from [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data) and then filtered, cleaned, and pre-processed by our team
* COVID data for most Utah counties was collected and filtered from [NY Times](https://github.com/nytimes/covid-19-data) and then filtered, cleaned, and pre-processed by our team
* Initial county adjacency data was collected from the [US Census Bureau](https://www.census.gov/geographies/reference-files/2010/geo/county-adjacency.html) and then filtered, cleaned, and pre-processed by our team
* Initial great-circle distance data for adjacent counties was collected from the [National Bureau of Economic Research](https://www.nber.org/research/data/county-distance-database) and then filtered, cleaned, and pre-processed by our team
* Initial driving distance and duration data for adjacent counties was gathered with the [Distance Matrix API](https://distancematrix.ai/dev) and then filtered, cleaned, and pre-processed by our team
* COVID patient symptom data was collected from an article published in the [npj Digiral Medicine Journal](https://www.nature.com/articles/s41746-020-00372-6)

Mid-Points
-----------------
This folder contains intermediate data files used (most of which come from the Data_Preparation_and_Pre_Processing.ipyn notebook)
