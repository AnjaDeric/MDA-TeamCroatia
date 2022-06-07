# MDA-TeamCroatia
Modern Data Analytics Final Project

This repository contains all python scripts, notebooks, and data files used to create the Team Croatia final project for Modern Data Analytics.

File Descriptions
-----------------
**Data_Preparation_and_Pre_Processing.ipynb**: Google Colab notebook used for most of our data preparation, cleaning, and pre-processing. This includes gathering and cleaning of county-related information, COVID case data (initial testing), county adjacency/border information, and county distance information.

**covid_data.py**: The final Python script which contains functions to get COVID case data from our data sources. 

**main.py**: The final Python script which makes use of the covid_data.py functions to collect COVID data for a specified range of dates and push the files to our GitHub.

**active_cases.csv**: CSV file containing active COVID case counts for all counties. This file is updated every time main.py runs, including all dates from 1/1/2021 up until the day before the moment when the script is run. 

**SymptomResultPrediction.ipynb**: Google Colab notebook used to create and test machine learning models to predict COVID test results based on symptoms.

**Py2neo (Neo4j Jupyter Code).ipynb**: Google Colab notebook used to calculate shortest and safest path using COVID data in neo4j.

Data Folder
-----------------
The Data folder in this repository contains all the csv files used as intermediate stopping points. The file descriptions can be found inside the folder itself.
