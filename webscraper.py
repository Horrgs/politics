import requests
from bs4 import BeautifulSoup
import csv

url = 'https://www.house.gov/representatives'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find('div', class_='view-content')
states = results.find_all('table', class_='table')

p = 0
with open('congress.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["First Name", "Last Name", "State", "C.D.", "Party", "Phone Number"])
    for i in states:
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

