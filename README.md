# St. Louis NIBRS Criem Database

## Overview:
This project creates a comprehensive database containing NIBRS data on all crimes committed within the city of St. Louis, Missouri beginning from January 1, 2021, the date from which all law enforcement agencies were required to switch from UCR SRS crime reporting to the current NIBRS system. Because of the different reporting standards, comparisons to crime rates prior to 2021 is highly discouraged.

## Background:
I was working with a St. Louis non-profit that needed crime data within a specific geographic area in St. Louis. Unfortunately, the crime data that is made available by SLMPD is limited: there are PDFs with monthly totals by neighborhood and category, as well as CSVs with more detailed monthly "updates". But the CSVs are snapshots--a mix of new crimes committed in the current month, as well as updates/changes to cases that occurred in previous months--which is only useful if you have all of the prior data. In order to make the data useful, I needed to create a comprehensive database that would automatically add new crime data and update previous crimes as more information was reported. Since I felt that this was data others might find useful, I decided to make the entire database available to the public.

## Data Overview:
The database includes all reported crime incidents in the city of St. Louis (does not include St. Louis county). The raw data comes from the St. Louis Metropolitan Police Department, which posts monthly updates [here](https://www.slmpd.org/crime_stats.shtml). The current database contains over 200,000 rows and 21 features. All crime incidents that are determined by the SLMPD to be "unfounded" are stored in a separate table.

## Next Steps:
I am working to create a webpage that will provide CSV downloads of the database to users. Currently, the project is set up as a flask app that uses Bootstrap JS to style the frontend. The project uses a SQLite database for the time being, but will be migrating to Postgres once the webpage is live.
