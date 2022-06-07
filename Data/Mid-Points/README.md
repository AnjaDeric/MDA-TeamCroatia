This folder contains all intermediate CSV files and data used and generated in the data collection, cleaning, and pre-processing steps of the project.

File Desctiptions
-----------------
**GC_distances**: contains a list of pairs of relavant counties that border each other and the Great_Circle distances between them

**adj_dist_all_raw.csv**: contains a list of pairs of relavant counties that border each other and the Great_Circle distances, driving ditances, and driving durations between them (this version is NOT cleaned + contains some missing values)

**adj_dist_all_raw_copy.csv**: contains a list of pairs of relavant counties that border each other and the Great_Circle distances, driving ditances, and driving durations between them (this version is NOT cleaned but does not contain missing values)

**adj_distances_GC**: contains a list of pairs of relavant counties that border each other and the Great_Circle distances between them

**adjacent_counties**: contains data about which (all) US counties border each other; this data set was downloaded from the Census Bureau ([link](https://www.census.gov/geographies/reference-files/2010/geo/county-adjacency.html)) and loaded in as a CSV file (but it has not been cleaned yet)

**adjacent_counties_corrected**: contains a list of pairs of relevant counties that border each other; this is the cleaned version of the adjacent_counties file and additioanlly only contains the relevant counties

**county_info_with_key**: contains a list of relevant US counties and basic info about them (FIPS, name, state, longitude, latitude, population)

**covid_data_clean**: contains basic information and _cumulative_ case counts for all relevant counties for December 22nd of 2020 through December 31st of 2021 (cleaned, no missing values)

**covid_data_raw**: contains  _cumulative_ case counts for all relevant counties for December 22nd of 2020 through December 31st of 2021 (not cleaned, contains missing values)

**covid_data_raw_nts**: contains basic information and _cumulative_ case counts for all relevant counties for December 22nd of 2020 through December 31st of 2021 (not cleaned, contains missing values, different column date format)

**state_info**: contains a list of US states (excluding Alaska and Hawaii) and their FIPS, latitude, longitude, and population

