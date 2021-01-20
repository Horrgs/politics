import requests
from bs4 import BeautifulSoup
import csv
from itertools import groupby
from datetime import datetime
import re


def get_donations():
    url = ('https://cfapp.elections.ny.gov/ords/plsql_browser/CONTRIBUTORA_COUNTY?ID_in=C87477&' +
           'date_From=01/01/2006&date_to=01/15/2021&AMOUNT_From=1&AMOUNT_to=10000000&ZIP1=00501&' +
           'ZIP2=99950&ORDERBY_IN=N&CATEGORY_IN=ALL')
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    donations = soup.find_all('tr')
    headers = [e.string.lower() for e in donations[1].find_all('th')]
    total = str(list(filter(None, [p.string.strip() for p in donations[-1]]))[-1])
    donations = donations[2:-1]
    data_set = []
    for donation in donations:
        attr = donation.find_all('td')
        entry = {}
        for header_name, header_value in zip(headers, attr):
            if header_name == "contr. date":
                header_name = "contr_date"

            elif header_name == "amt":
                header_name = "amount"
            if header_name != "contributor":
                print(type(header_value.text))
                entry[header_name] = str(header_value.text).strip()
            if header_name == "contributor":
                for i in header_value:
                    i = [str(y).strip() for y in i if "<br/>" not in str(y).strip()]
                    entry['name'] = i[0]
                    entry['address'] = i[1]
                    entry['locale'] = i[2]

        data_set.append(entry)
    total_donations = {k: "" for k, v in data_set[0].items()}
    total_donations['name'] = "TOTAL DONATIONS"
    total_donations['amount'] = total
    print(total_donations)
    data_set.append(total_donations)
    return data_set

def sort_politics(response):
    total_contr = response[-1]['amount']
    print(total_contr)
    del response[-1]
    sorted = []

    print(response)
    """for k, v in groupby(response, key=lambda x: x['contributor']):
        contributions = list(v)
        r = {x:0 for x in response[0].keys()}
        r['contributor'] = contributions[0]['contributor']
        r['recipient'] = contributions[0]['recipient']
        #name = re.findall(r'', r['contributor'])
        earliest_date = datetime.strptime(contributions[0]['contr_date'], '%d-%b-%y')
        recent_date = earliest_date
        for contribution in contributions:
            date_of_contr = datetime.strptime(contribution['contr_date'], '%d-%b-%y')
            if date_of_contr > recent_date:
                recent_date = date_of_contr
            if date_of_contr < earliest_date:
                earliest_date = date_of_contr
            r['amount'] = r['amount'] + float(contribution['amount'].replace(",", ""))
        if earliest_date == recent_date:
            r['contr_date'] = ("{0}".format(earliest_date.strftime("%d-%b-%y")))
        else:
            r['contr_date'] = ("{0}\n -\n{1}".format(earliest_date.strftime("%d-%b-%y"), recent_date.strftime("%d-%b-%y")))
        sorted.append(r)"""
    return sorted


def write_csv(donations):
    with open('campaign_donations.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, donations[0].keys())
        writer.writeheader()
        writer.writerows(donations)


write_csv(get_donations())
