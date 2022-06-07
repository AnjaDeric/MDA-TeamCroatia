import pandas as pd
import numpy as np
from datetime import date, timedelta


def get_covid_cases(start_date, end_date=None, type_cases='confirmed', county_fips=None, scale=True):
    """Returns a dataframe specifying daily COVID active cases or COVID deaths
    scaled by population

    Parameters
    ----------
    start_date : str
        The first date that cases/deaths should be reported for
    end_date : str, optional
        The last date that cases/deaths should be reported for (default is None,
        in which case only the start_date gets reported)
    type_cases : str, optional
        Choice of COVID cases or deaths to be reported (default is 'confirmed',
        which reports COVID cases)
    county_fips: numpy array, optional
        Array of county FIPS for which cases/deaths should be reported for
        (default is None and all counties get reported)
    scale: bool, optional
        Indicates if data should be scaled by populations (default is True)

    Returns
    -------
    active: dataframe
        a dataframe of specified counties in the specified time frame with
        COVID active cases or deaths scaled by population (per 100,000 people)
    """

    # if end date is not specified, assume we are looking for only one date
    if end_date is None:
        end_date = start_date

    # since raw data contains cumulative cases/deaths, we must consider:
    # when counting active cases, we consider 10 days prior (case is active for 10 days)
    # when counting deaths, we only look at difference from the last day
    days_behind = 10
    if type_cases == 'deaths':
        days_behind = 1

    # get a new start_date based on how many days prior we must look at
    start_date_new = date(int('20' + start_date.split('/')[2]), int(start_date.split('/')[0]),
                          int(start_date.split('/')[1])) - timedelta(days=days_behind)
    start_date_new = str(start_date_new.month) + '/' + str(start_date_new.day) + '/' + str(start_date_new.year)[-2:]

    # get information on all potential counties from GitHub
    county_info = pd.read_csv(
        'https://raw.githubusercontent.com/AnjaDeric/MDA-TeamCroatia/main/Data/county_info.csv')
    county_info['fips'] = county_info['fips'].apply('{:0>5}'.format)

    # if county FIPS are not specified, we consider all counties
    if county_fips is None:
        county_fips = county_info['fips'].unique()

    # get cumulative and daily cases/deaths
    cumulative = get_cumulative(start_date_new, end_date, county_fips, type_cases)
    daily = get_daily_diff(cumulative)
    active = daily.copy()

    # if counting cases (not deaths), we additionally get rolling sum over 10 days
    if type_cases == 'confirmed':
        active = get_active_cases(daily)

    # scale data by population
    if scale:
        active = scale_by_pop(active, county_info)

    # change FIPS of one DS county to match format for mapbox (used later for plotting)
    active['fips'].replace({'46102': '46113'}, inplace=True)

    return active


def get_cumulative(start_date, end_date, county_fips, type_cases):
    """Returns a dataframe of cumulative COVID cases or deaths (collected from
    Johns Hopkins)

    Parameters
    ----------
    start_date : str
        The first date that cases/deaths should be reported for
    end_date : str
        The last date that cases/deaths should be reported for (default is None,
        in which case only the start_date gets reported)
    type_cases : str
        Choice of COVID cases ('confirmed') or deaths ('deaths') to be reported
    county_fips: numpy array
        Array of county FIPS for which cases/deaths should be reported for

    Returns
    -------
    covid_data: dataframe
        a dataframe of specified counties in the specified time frame with
        COVID cumulative cases or deaths
    """

    # read raw data from johns Hopkins GitHub
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/' \
          'csse_covid_19_data/csse_covid_19_time_series/' \
          'time_series_covid19_' + type_cases + '_US.csv'
    covid_data = pd.read_csv(url)

    # fill in missing FIPS with 0s and format to 5 digits
    covid_data['FIPS'] = covid_data['FIPS'].fillna(0)
    covid_data.FIPS = (covid_data.FIPS.astype(int)).astype(object)
    covid_data['FIPS'] = covid_data['FIPS'].apply('{:0>5}'.format)
    covid_data.rename(columns={'FIPS': 'fips'}, inplace=True)

    # drop all dates and columns we don't need
    covid_data = pd.concat([covid_data['fips'], covid_data.loc[:, start_date:end_date]], axis=1)

    # only keep rows were FIPS matches one of the ones we want
    covid_data = covid_data[covid_data['fips'].isin(county_fips)]

    # from previous analysis, these are all the FIPS codes with missing/incorrect data
    # these counties all have cases set to 0, when that is not actually true
    missing_fips = np.array(['49001', '49003', '49005', '49007', '49009', '49013', '49015',
                             '49017', '49019', '49021', '49023', '49025', '49027', '49029',
                             '49031', '49033', '49039', '49041', '49047', '49053', '49055',
                             '49057'], dtype=object)

    # check if any of our counties of interest are in this set
    missing_fips = np.intersect1d(missing_fips, county_fips)

    # if so, fill in the missing data
    if missing_fips.size != 0:
        # drop these counties from the dataset temporarily
        missing_counties = covid_data[covid_data['fips'].isin(missing_fips)]
        covid_data.drop(covid_data.loc[covid_data['fips'].isin(missing_fips)].index, inplace=True)

        # fill in the missing/incorrect data and merge back with the rest of the data set
        missing_counties = fill_missing_vals(missing_counties, start_date, end_date, missing_fips, type_cases)
        covid_data = pd.concat([covid_data, missing_counties], ignore_index=True)
        covid_data.reset_index(inplace=True, drop=True)

    return covid_data


def fill_missing_vals(missing_counties, start_date, end_date, missing_fips, type_cases):
    """Returns a dataframe of cumulative COVID cases or deaths for only the
    specified missing counties (collected from NY Times)

    Parameters
    ----------
    missing_counties: dataframe
        A dataframe of counties with missing/incorrect cumulative data
    start_date : str
        The first date that cases/deaths should be reported for
    end_date : str
        The last date that cases/deaths should be reported for (default is None,
        in which case only the start_date gets reported)
    missing_fips: numpy array
        An array of county FIPS with missing/incorrect cumulative data
    type_cases : str
        Choice of COVID cases ('confirmed') or deaths ('deaths') to be reported

    Returns
    -------
    missing_counties: dataframe
        A dataframe of missing counties in the specified time frame with
        COVID cumulative cases or deaths
    """

    # get a list of all years we will need to look at
    year_range = list(range(int(start_date[-2:]), int(end_date[-2:]) + 1))

    # get a list of all dates we will need
    case_cols = (missing_counties.columns[1:]).tolist()

    # start with a dataframe with only the missing FIPS codes
    missing_counties = missing_counties[['fips']]

    # for each year needed, get the NY Times data and add on to the missing data frame
    for year in year_range:
        times_data = extract_times_data('20' + str(year), case_cols, missing_fips, type_cases)
        missing_counties = pd.merge(missing_counties, times_data, on='fips', how='left')

    # fill in any missing values with 0 (for dates in 2020 when COVID was just starting)
    missing_counties = missing_counties.fillna(0)

    return missing_counties


def extract_times_data(year, case_cols, missing_fips, type_cases):
    """ Extracts missing data and returns a dataframe of cumulative COVID
    cases or deaths for only the specified missing counties (collected from NY Times)

    Parameters
    ----------
    year: str
        Year that the data needs to be collected for
    case_cols : list
        A list of dates within the year that data needs to be collected for
    missing_fips: numpy array
        An array of county FIPS with missing/incorrect cumulative data
    type : str
        Choice of COVID cases ('confirmed') or deaths ('deaths') to be reported

    Returns
    -------
    nytimes_wide: dataframe
        A dataframe of missing counties for the specified year and dates with
        COVID cumulative cases or deaths
    """

    # access and read in the file for the correct year
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/' \
          'us-counties-' + year + '.csv'
    nytimes = pd.read_csv(url)

    # reformat FIPS to match 5-digit format
    nytimes['fips'] = nytimes['fips'].fillna(0)
    nytimes.fips = (nytimes.fips.astype(int)).astype(object)
    nytimes['fips'] = nytimes['fips'].apply('{:0>5}'.format)

    # get only rows with missing Utah counties
    nytimes = nytimes[nytimes['fips'].isin(missing_fips)]

    # change date to format used for covid_data columns and only keep the dates we need
    nytimes['date'] = nytimes.date.str[5:7].astype(int).astype(str) + '/' + nytimes.date.str[8:10].astype(int).astype(
        str) + '/' + nytimes.date.str[2:4].astype(int).astype(str)
    nytimes = nytimes[nytimes['date'].isin(case_cols)]

    # transform into wide table and add FIPS code
    if type_cases == 'confirmed':
        nytimes_wide = nytimes.pivot(index='fips', columns='date', values='cases')
    else:
        nytimes_wide = nytimes.pivot(index='fips', columns='date', values='deaths')
    nytimes_wide.reset_index(inplace=True)

    return nytimes_wide


def get_daily_diff(covid_data):
    """Returns a dataframe of daily change in COVID cases or deaths based
    on cumulative data

    Parameters
    ----------
    covid_data: dataframe
        A dataframe containing cumulative case counts

    Returns
    -------
    covid_data: dataframe
        A modified dataframe containing daily counts of new cases or deaths
    """

    # calculate change in cases for all columns except FIPS
    covid_data.loc[:, covid_data.columns != 'fips'] = covid_data.loc[:, covid_data.columns != 'fips'].diff(axis=1)

    # set all negative values to 0 (errors in cumulative data)
    case_cols = (covid_data.columns[1:]).tolist()
    covid_data[case_cols] = covid_data[case_cols].mask(covid_data[case_cols] < 0, 0)

    # remove first column after FIPS (since it will be NaN)
    covid_data.drop([covid_data.columns[1]], axis=1, inplace=True)

    return covid_data


def get_active_cases(covid_data):
    """Returns a dataframe of active COVID cases based on daily new cases,
    assuming a case is active for 10 days

    Parameters
    ----------
    covid_data: dataframe
        A dataframe containing daily new case counts

    Returns
    -------
    covid_data: dataframe
        A modified dataframe containing daily active cases (assuming
        a 10-day active period of the virus)
    """

    # get active cases by summing up new cases over 10 days
    # (assuming a case is active for 10-days by CDC rules)
    covid_data.loc[:, covid_data.columns != 'fips'] = covid_data.loc[:, covid_data.columns != 'fips'].rolling(
        10, axis=1).sum()

    # drop columns we don't need
    covid_data.drop(covid_data.iloc[:, 1:10], axis=1, inplace=True)

    return covid_data


def scale_by_pop(covid_data, county_info):
    """Returns a dataframe of case/death counts scaled by population of each
    county (units returned: per 100,000 people)

    Parameters
    ----------
    covid_data: dataframe
        A dataframe containing case/death counts
    county_info: dataframe
        A dataframe containing all included counties and their population

    Returns
    -------
    covid_data: dataframe
        A modified dataframe containing scaled case or death counts
        (with units per 100,000 people)
    """

    # add population data to dataframe
    covid_data = pd.merge(county_info[['fips', 'population']], covid_data, on='fips', how='right')

    # scale active cases by population * 100,000 (to get cases per 100,000 people)
    covid_data.iloc[:, 2:] = covid_data.iloc[:, 2:].div(covid_data.population, axis=0)*100000
    covid_data.drop(['population'], axis=1, inplace=True)

    return covid_data

