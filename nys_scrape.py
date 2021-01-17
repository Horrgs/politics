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

    results = soup.find('div', id='cfContent')
    donations = soup.find_all('tr')
    headers = [str(e.string).lower() for e in donations[1].find_all('th')]
    donations = donations[2:]
    data_set = []
    for donation in donations:
        attr = donation.find_all('td')
        individual = {}
        for header_name, header_value in zip(headers, attr):
            if header_name == "contr. date":
                header_name = "contr_date"
            elif header_name == "amt":
                header_name = "amount"
            individual[header_name] = " ".join(header_value.text.split())
            if header_name == "contributor":
                x = header_value.find_all('font')
                for i in x:
                    print(i.contents)
        data_set.append(individual)
    return data_set

def sort_politics(response):
    total_contr = response[-1]['amount']
    print(total_contr)
    del response[-1]
    sorted = []
    for k, v in groupby(response, key=lambda x: x['contributor']):
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
        sorted.append(r)
    return sorted



def write_csv(donations):
    with open('campaign_donations.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, donations[0].keys())
        writer.writeheader()
        writer.writerows(donations)


write_csv(sort_politics(get_donations()))

"""p = 0
with open('campaign_donations.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Contributor", "Amount", "Date of Donation", "Recipient", "Date of Report to F.E.C."])
    for i in donations:
        state_name = i.find('caption').text.strip()

        members = i.find('tbody').find_all('tr')
        print(state_name)

        for member in members:
            district, name, party, office, phone, assignment = [e.text.strip() for e in member.find_all('td')]
            if ',' in name:
                kr = name.split(",")
                first_name = kr[1].strip()
                last_name = kr[0].strip()
            else:
                first_name = name
                last_name = ""
            writer.writerow([first_name, last_name, state_name, district, party, phone])

"""