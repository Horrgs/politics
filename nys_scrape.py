import requests
from bs4 import BeautifulSoup
import csv
from itertools import groupby
from datetime import datetime
import re
from enum import Enum

class SearchType(Enum):
    CONTRIBUTOR = 0
    EXPENSES = 1


def get_donations(search_type: SearchType, candidate_id):
    url = ('https://cfapp.elections.ny.gov/ords/plsql_browser/{0}A_COUNTY?ID_in={1}&' +
           'date_From=01/01/2006&date_to=01/15/2021&AMOUNT_From=1&AMOUNT_to=10000000&ZIP1=00501&' +
           'ZIP2=99950&ORDERBY_IN=N').format(search_type.name, candidate_id.strip())
    if search_type == SearchType.CONTRIBUTOR:
        url += "&CATEGORY_IN=ALL"
    elif search_type == SearchType.EXPENSES:
        url += "&OFFICE_in=ALL"

    print(url)
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
            if header_name != "contributor" and header_name.replace("/", "").lower() != "payeerecipient":
                entry[header_name] = header_value.text.strip()
            if header_name == "contributor" or header_name.replace("/", "").lower() == "payeerecipient":
                for i in header_value:
                    i = [str(y).strip() for y in i if "<br/>" not in str(y).strip()]
                    entry['name'] = i[0]
                    entry['address'] = i[1]
                    entry['locale'] = i[2]

        data_set.append(entry)
    total_donations = {k: "" for k, v in data_set[0].items()}
    total_donations['name'] = "TOTAL {0}".format(search_type.name)
    total_donations['amount'] = total
    data_set.append(total_donations)
    return data_set


def sort_politics(response):
    total_contr = response[-1]['amount']
    print(total_contr)
    del response[-1]
    names = [v for dic in response for k, v in dic.items() if k == 'name']
    first_name = names[0]
    second_name = ""
    for name in names:
        if name == first_name:
            continue
        if name >= second_name:
            second_name = name
        elif name <= second_name:
            second_name = name
            break
        continue
    businesses = response[0:names.index(second_name)]
    individuals = response[names.index(second_name):]
    businesses_ = []
    for k, v in groupby(businesses, key=lambda x: x['address']):
        contributions = list(v)
        print(k)
        r = {x: y for x, y in contributions[0].items()}
        r['amount'] = 0
        r.pop('name', None)
        r['names'] = []
        r['recipient'] = contributions[0]['recipient']
        earliest_date = datetime.strptime(contributions[0]['contr_date'], '%d-%b-%y')
        recent_date = earliest_date
        for contribution in contributions:
            if contribution['name'] not in r['names']:
                r['names'].append(contribution['name'])
            date_of_contr = datetime.strptime(contribution['contr_date'], '%d-%b-%y')
            if date_of_contr > recent_date:
                recent_date = date_of_contr
            if date_of_contr < earliest_date:
                earliest_date = date_of_contr
            r['amount'] = r['amount'] + float(contribution['amount'].replace(",", ""))
        if earliest_date == recent_date:
            r['contr_date'] = ("{0}".format(earliest_date.strftime("%d-%b-%y")))
        else:
            r['contr_date'] = (
                "{0}\n -\n{1}".format(earliest_date.strftime("%d-%b-%y"), recent_date.strftime("%d-%b-%y")))
        businesses_.append(r)
    print(businesses_)
    return businesses_


def write_csv(search, donations, po_id):
    with open('campaign_{0}_{1}.csv'.format(search, po_id), 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, donations[0].keys())
        writer.writeheader()
        writer.writerows(donations)


sort_politics(get_donations(SearchType.CONTRIBUTOR, "C87477"))


"""
if __name__ == '__main__':
    print("Welcome to NYS Campaign Contribution and Expenditure search")
    c_or_e = None
    while True:
        try:
            print("\n")
            c_or_e = input("Would you like to search campaign contributions, expenditures, or both?\n" +
                           "Enter C for contributions, E for expenditures, or B for both.\n" +
                           "Not case sensitive.")
            if c_or_e.lower() != "c" and c_or_e.lower() != "e" and c_or_e != "b":
                raise ValueError
        except ValueError:
            print("Sorry, I didn't understand that.")
            continue
        else:
            break
    print("\n\n\n")
    while True:
        print("This next part requires some work on your part. Head to \n" +
              "https://cfapp.elections.ny.gov/ords/plsql_browser/all_filers and use CTRL+F to search for \n"
              "the person of interest.")
        print("Alternatively, an easier method is to search by county. This is limited to ACTIVE filers.")
        print("Link here: https://www.elections.ny.gov/regbycounty.html")
        print("Copy and paste their unique ID, which will be the first line above their name.")
        print("It should look like C01065 or A01065")
        print("NOTE: A candidate may have more than one ID, separate them with commas as such:")
        print("C01065, A01065")
        candidate_id = input("Enter the candidate ID:")
        if ',' in candidate_id:
            candidate_id = candidate_id.split(",")
            for c_id in candidate_id:
                c_id = c_id.strip()
                if re.match('^[a-zA-Z0-9_]{6}$', c_id):
                    if c_or_e.lower() == 'c':
                        write_csv('contributions', get_donations(SearchType.CONTRIBUTOR, c_id), c_id)
                    elif c_or_e.lower() == 'e':
                        write_csv('expenses', get_donations(SearchType.EXPENSES, c_id), c_id)
                    elif c_or_e.lower() == 'b':
                        write_csv('contributions', get_donations(SearchType.CONTRIBUTOR, c_id), c_id)
                        write_csv('expenses', get_donations(SearchType.EXPENSES, c_id), c_id)
                else:
                    print("Sorry, I didn't understand that.")
                    continue
        else:
            candidate_id = candidate_id.strip()
            if re.match('^[a-zA-Z0-9_]{6}$', candidate_id):
                if c_or_e.lower() == 'c':
                    write_csv('contributions', get_donations(SearchType.CONTRIBUTOR, candidate_id), candidate_id)
                elif c_or_e.lower() == 'e':
                    write_csv('expenses', get_donations(SearchType.EXPENSES, candidate_id), candidate_id)
                elif c_or_e.lower() == 'b':
                    write_csv('contributions', get_donations(SearchType.CONTRIBUTOR, candidate_id), candidate_id)
                    write_csv('expenses', get_donations(SearchType.EXPENSES, candidate_id), candidate_id)
            else:
                print("Sorry, I didn't understand that.")
                continue
        break
"""