This folder contains all CSV files and data used and generated in the data collection, cleaning, and pre-processing steps of the project. These files are as follows:

**active_cases_2021**: contains basic information and _active_ case counts for all relevant counties for January 1st through December 31st of 2021 (cleaned, no missing values)

**adj_distances_GC**: contains a list of pairs of relavant counties that border each other and the Great_Circle distances between them

**adjacent_counties**: contains data about which (all) US counties border each other; this data set was downloaded from the Census Bureau ([link](https://www.census.gov/geographies/reference-files/2010/geo/county-adjacency.html)) and loaded in as a CSV file (but it has not been cleaned yet)

**adjacent_counties_corrected**: contains a list of pairs of relevant counties that border each other; this is the cleaned version of the adjacent_counties file and additioanlly only contains the relevant counties

**county_info**: contains a list of relevant US counties and basic info about them (FIPS, name, state, longitude, latitude, population)

**covid_data_clean**: contains basic information and _cumulative_ case counts for all relevant counties for Devember 25th of 2020 through December 31st of 2021 (cleaned, no missing values)

**covid_data_raw**: contains basic information and _cumulative_ case counts for all relevant counties for Devember 25th of 2020 through December 31st of 2021 (not cleaned, contains missing values)

**state_info**: contains a list of US states (excluding Alaska and Hawaii) and their FIPS, latitude, longitude, and population

Notes: 
* the term _relevant_ counties implies that all US territories as well as Alaska, Hawaii, and any island counties in the continental US have been filtered out from the data set
* all COVID data (including county_info and state_info) was collected and filtered from [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data) and then filtered, cleaned, and pre-processed by our team
