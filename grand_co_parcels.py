# Grand County Parcel data scraper

import csv
import requests
import time
from bs4 import BeautifulSoup
from urllib import parse

# Grand County Assessor Data web scraper
# procedure:
#  1 enter a parcel number on the main search form:
#    http://tax.grandcountyutah.net/grandcountyutah/list-page.php
#  2 on the search results page, get the link to the parcel details page
#  3 extract the ownership data from the table in the details page


# input file
infile = 'parcels.txt'

# output file
outfile = 'parcel_owners.csv'

# list stores the lists of parcel details
allrows = []

# Grand County Assessor website URLS
# parcel search URL
gc_search_url = 'http://tax.grandcountyutah.net/grandcountyutah/list-page.php'

#parcel data page base URL
gc_base_url = 'http://tax.grandcountyutah.net/grandcountyutah/'


def get_parcel_list():
    '''
    Opens a text file, with a parcel ID number on each row.
    returns a list of parcel IDs
    '''

    parcelnos = []

    with open(infile, 'r') as input:
        for line in input:
            parcelnos.append(line.strip()) # strip off the newline char

    return parcelnos


def request_details(parcelno):
    # gets the details of a parcel from the Assessor site
    # returns values as a list

    print("parcel:", parcelno)
    time.sleep(5) # wait 5 seconds to avoid server issues

    # Requests parameters
    payload = {'search': parcelno}

    # send HTTP GET with search param
    req_search = requests.get(gc_search_url, params=payload)

    # open response as text for parsing in BeautifulSoup
    soup_search = BeautifulSoup(req_search.text, 'html.parser')

    # get the first <a> in the search response page, which links to parcel info page
    data = soup_search.table.tbody.td.a
    a = soup_search.table.tbody.td.a['href']

    # construct the full URL of parcel details page
    results = parse.urljoin(gc_base_url, a)

    # send HTTP request for parcel details
    req_result = requests.get(results)

    # open response as text for parsing in BeautifulSoup
    req_soup = BeautifulSoup(req_result.text, 'html.parser')

    # get the parcel detail rows from the table
    rows = req_soup.table.find_all('tr')

    rowlist = []
    for row in rows:

        # desired table rows are of the class .table_inner
        # undesired table rows do not appear to have a class

        if row.td.has_attr('class'):

            if 'table_inner' in row.td['class']:

                # get all the td data fields in the current row
                tuple = row.find_all('td')

                # append each table row's value to the list of fields for that row
                rowlist.append(tuple[1].string)

    return rowlist


headers = [
    'parcel',
    'serial_no',
    'entry',
    'owner_name_1',
    'owner_name_2',
    'address_1',
    'address_2',
    'city',
    'state',
    'zip',
    'district',
    'status',
    'prop_addr',
    'prop_city',
    'messages',
    'backtax_stat',
    'backtax_amt',
    'backtax_intr'
    ]


parcels = get_parcel_list()

with open(outfile, 'w', newline='') as out:
    # open output to write CSV
    cf = csv.writer(out)
    cf.writerow(headers)

    # get the parcel details and append the values to the list of values list
    for parcel in parcels:

        details = request_details(parcel)

        if details:
            cf.writerow(details)
        else:
            t = [''] * 18
            t[0] = parcel
            cf.writerow(t)


print("done")
