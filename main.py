from covid_data import get_covid_cases
import pandas as pd
from datetime import date, timedelta
from github import Github
from github import InputGitTreeElement

if __name__ == '__main__':
    # get general county information
    county_info = pd.read_csv(
        'https://raw.githubusercontent.com/AnjaDeric/MDA-TeamCroatia/main/Data/county_info.csv')
    county_info['fips'] = county_info['fips'].apply('{:0>5}'.format)

    # format yesterday's date
    today = str(date.today()-timedelta(days=1))
    today = str(int(today.split('-')[1])) + '/' + str(int(today.split('-')[2])) + '/' + \
            today.split('-')[0][2:]

    # get cases up until yesterday (do not scale by population)
    cases = get_covid_cases(start_date='1/1/21', end_date=today, scale=False)

    # update column names to match old format
    cases.columns = ['fips'] + ['d' + '{:0>2}'.format(d.split('/')[0]) +
                                '{:0>2}'.format(d.split('/')[1]) +
                                '20' + d.split('/')[2] for d in cases.columns[1:]]

    # merge county information with case counts and save to csv
    cases = pd.merge(county_info, cases, on="fips", how="left")

    # change FIPS of one DS county to match format for mapbox (used later for plotting)
    cases.loc[cases.fips == '46102', 'fips'] = '46113'

    cases.to_csv('active_cases.csv', index=False)
    cases_csv = cases.to_csv(sep=',', index=False)

    # files and names to upload to GitHub
    file = cases_csv
    file_name = 'active_cases_test.csv'

    # GitHub commit message
    commit_message = 'daily active case update'

    # create connection with GiHub and select repo and branch
    g = Github('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')
    repo = g.get_user().get_repo('MDA-TeamCroatia')
    master_ref = repo.get_git_ref("heads/main")
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)

    # create list of all elements to commit
    element_list = list()
    element = InputGitTreeElement(file_name, '100644', 'blob', file)
    element_list.append(element)
    tree = repo.create_git_tree(element_list, base_tree)

    # commit file to GitHub
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)

    # print success message
    print('Update complete')


